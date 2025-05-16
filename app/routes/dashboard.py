from flask import Blueprint, jsonify, render_template, request
from flask_login import login_required, current_user
from sqlalchemy import func
from app.models import FuelType, PriceRecord, Station, UploadBatch
import pandas as pd
from app import db
from app.utils.station_loader import load_wa_stations
import numpy as np

dashboard_bp = Blueprint(
    'dashboard',
    __name__,
    url_prefix='/dashboard',
    template_folder="../../templates/main"
)

@dashboard_bp.route('/')
@login_required
def dashboard_home():
    # load basic station geodata
    load_wa_stations()

    # —— 1. Get the latest batch —— 
    last_batch = (
        UploadBatch.query
        .filter_by(user_id=current_user.id)
        .order_by(UploadBatch.uploaded_at.desc())
        .first()
    )
    if not last_batch:
        empty = {'labels': [], 'datasets': []}
        default_metrics = {
            'avg_price':   "$0.00",
            'volatility':  "0.00%",
            'cheapest':    "$0.00",
            'expensive':   "$0.00"
        }
        return render_template('main/dashboard.html',
                               user=current_user,
                               chart_data={'daily': empty, 'weekly': empty, 'monthly': empty},
                               fuel_types=['All Fuel Types'],
                               locations=['All Locations'],
                               metrics=default_metrics)

    # —— 2. From DB to dataframe —— 
    qry = (
        db.session.query(
            PriceRecord.date.label('publish_date'),
            FuelType.name.label('fuel_type'),
            PriceRecord.price.label('price'),
            Station.suburb.label('location')
        )
        .join(FuelType, PriceRecord.fuel_type_id == FuelType.id)
        .join(Station, PriceRecord.station_id == Station.id)
        .filter(PriceRecord.batch_id == last_batch.id)
    )
    
    sql_str = str(qry.statement.compile(compile_kwargs={"literal_binds": True}))
    df = pd.read_sql_query(sql=sql_str, con=db.engine, parse_dates=['publish_date'])
 
    df['date_str']  = df['publish_date'].dt.strftime('%Y-%m-%d')
    df['week_str']  = 'Week ' + df['publish_date'].dt.isocalendar().week.astype(str)
    df['month_str'] = df['publish_date'].dt.strftime('%Y-%m')

    fuel_types = FuelType.query.order_by(FuelType.name).all()
    locations  = ['All Locations']    + sorted(df['location'].unique().tolist())
    sel_fuel = request.args.get('fuel_type', 'All Fuel Types')
    sel_loc  = request.args.get('location',  'All Locations')
    sel_date = request.args.get('date')

    df_f = df
    if sel_fuel != 'All Fuel Types':
        df_f = df_f[df_f['fuel_type'] == sel_fuel]
    if sel_loc != 'All Locations':
        df_f = df_f[df_f['location'] == sel_loc]
    if sel_date:
        df_f = df_f[df_f['date_str'] == sel_date]

    MAX_POINTS = 1000
    if len(df_f) > MAX_POINTS:
        df_f = df_f.sample(n=MAX_POINTS, random_state=42)

    def build_chart(dfg, by):
        labels = sorted(dfg[by].unique())
        datasets = []
        for ft in dfg['fuel_type'].unique():
            sub = dfg[dfg['fuel_type'] == ft]
            data = [ round(sub[sub[by]==lbl]['price'].mean(), 2)
                     if lbl in sub[by].values else None
                     for lbl in labels ]
            datasets.append({'label': ft, 'data': data, 'tension': 0.1})
        return {'labels': labels, 'datasets': datasets}

    chart_data = {
        'daily':   build_chart(df_f, 'date_str'),
        'weekly':  build_chart(df_f, 'week_str'),
        'monthly': build_chart(df_f, 'month_str'),
    }

    if not df_f.empty:
        avg_price   = df_f['price'].mean()
        volatility  = df_f['price'].std() * 100
        min_price   = df_f['price'].min()
        max_price   = df_f['price'].max()
    else:
        avg_price = volatility = min_price = max_price = 0

    metrics = {
        'avg_price':   f"${avg_price:.2f}",
        'volatility':  f"{volatility:.2f}%",
        'cheapest':    f"${min_price:.2f}",
        'expensive':   f"${max_price:.2f}"
    }

    return render_template('main/dashboard.html',
                           user=current_user,
                           chart_data=chart_data,
                           fuel_types=fuel_types,
                           locations=locations,
                           metrics=metrics)

@dashboard_bp.route('/data')
@login_required
def heatmap_data():
    sel_fuel = request.args.get('fuel_type')
    sel_loc  = request.args.get('location')
    sel_date = request.args.get('date')

    qry = (
        db.session.query(
            Station.latitude,
            Station.longitude,
            func.avg(PriceRecord.price).label('weight')
        )
        .join(PriceRecord, Station.id == PriceRecord.station_id)
        .filter(PriceRecord.batch.has(user_id=current_user.id))
    )

    if sel_fuel and sel_fuel != 'All Fuel Types':
        qry = qry.join(FuelType, PriceRecord.fuel_type_id == FuelType.id) \
                 .filter(FuelType.name == sel_fuel)

    if sel_loc and sel_loc != 'All Locations':
        qry = qry.filter(Station.suburb == sel_loc)

    if sel_date:
        try:
            from datetime import datetime
            date_obj = datetime.strptime(sel_date, '%Y-%m-%d').date()
            qry = qry.filter(PriceRecord.date == date_obj)
        except ValueError:
            pass

    qs = (
        qry
        .filter(
            Station.latitude.isnot(None),
            Station.longitude.isnot(None),
            Station.name.isnot(None),
        )
        .group_by(Station.id)
        .all()
    )

    MIN_LAT, MAX_LAT = -35.0, -13.5
    MIN_LNG, MAX_LNG = 112.9, 129.0

    points = []
    for lat, lng, w in qs:
        if lat is None or lng is None or w is None:
            continue
        if not (MIN_LAT <= lat <= MAX_LAT and MIN_LNG <= lng <= MAX_LNG):
            continue
        points.append([lat, lng, float(w)])

    return jsonify(points=points)


@dashboard_bp.route('/forecast')
@login_required
def get_forecast():
    sel_fuel = request.args.get('fuel_type')
    sel_loc  = request.args.get('location')
    algorithm = request.args.get('algorithm', 'linear')
    query_num = 50000

    qry = (
        db.session.query(PriceRecord.date.label('date'),
                         PriceRecord.price.label('price'))
        .join(FuelType, PriceRecord.fuel_type_id == FuelType.id)
        .join(Station, PriceRecord.station_id == Station.id)
        .filter(PriceRecord.batch.has(user_id=current_user.id))
    )

    if sel_fuel and sel_fuel != 'All Fuel Types':
        qry = (qry.filter(FuelType.name == sel_fuel))

    if sel_loc and sel_loc != 'All Locations':
        qry = (qry.filter(Station.suburb == sel_loc))

    rows = qry.order_by(PriceRecord.date.desc()).limit(query_num).all()
    if not rows:
        return jsonify(dates=[], historical=[], forecast=[])

    df = pd.DataFrame(rows, columns=['date','price'])
    df['date'] = pd.to_datetime(df['date'])

    df = (
        df.groupby('date', as_index=False)['price']
          .min()
          .sort_values('date')
    )

    if len(df) > 30:
        df = df.iloc[-30:]

    if df['date'].nunique() == 1:
        X = np.arange(len(df)).reshape(-1,1)
    else:
        X = (df['date'] - df['date'].min()).dt.days.values.reshape(-1,1)
    y = df['price'].values

    if algorithm == 'seasonal':
        from sklearn.linear_model import LinearRegression
        t = X.flatten() 
        sin7 = np.sin(2 * np.pi * t / 7)
        cos7 = np.cos(2 * np.pi * t / 7)
        X_seasonal = np.vstack([t, sin7, cos7]).T

        model = LinearRegression().fit(X_seasonal, y)

    elif algorithm == 'tree':
        from sklearn.tree import DecisionTreeRegressor
        model = DecisionTreeRegressor(max_depth=5).fit(X, y)
    else:  # default to linear
        from sklearn.linear_model import LinearRegression
        model = LinearRegression().fit(X, y)

    dates      = df['date'].dt.strftime('%Y-%m-%d').tolist()
    historical = np.round(y, 2).tolist()

    last_day   = df['date'].max()
    base_days  = (last_day - df['date'].min()).days if df['date'].nunique()>1 else 0
    future_idxs = np.arange(1,8).reshape(-1,1) + base_days

    future_dates = [
        (last_day + pd.Timedelta(days=i)).strftime('%Y-%m-%d')
        for i in range(1,8)
    ]

    if algorithm == 'seasonal':
        future_t = future_idxs.flatten()
        sin7_f = np.sin(2 * np.pi * future_t / 7)
        cos7_f = np.cos(2 * np.pi * future_t / 7)
        Xf = np.vstack([future_t, sin7_f, cos7_f]).T
        future_preds = model.predict(Xf).round(2).tolist()
    else:
        future_preds = model.predict(future_idxs).round(2).tolist()
    
    forecast = [
        {'date': d, 'price': p}
        for d, p in zip(future_dates, future_preds)
    ]

    return jsonify(dates=dates,
                   historical=historical,
                   forecast=forecast)

def _gather_dashboard_data(user_id,
                           fuel_type: str = "All Fuel Types",
                           location: str  = "All Locations",
                           filter_date: str = None):
    last_batch = (
        UploadBatch.query
        .filter_by(user_id=user_id)
        .order_by(UploadBatch.uploaded_at.desc())
        .first()
    )
    empty_chart = {"labels": [], "datasets": []}
    chart_data = {"daily": empty_chart, "weekly": empty_chart, "monthly": empty_chart}
    metrics = {
        "avg_price":   "$0.00",
        "volatility":  "0%",
        "cheapest":    "$0.00",
        "expensive":   "$0.00"
    }
    if not last_batch:
        return None, None
 
    qry = (
        db.session.query(
            PriceRecord.date.label('publish_date'),
            FuelType.name.label('fuel_type'),
            PriceRecord.price.label('price'),
            Station.suburb.label('location')
        )
        .join(FuelType, PriceRecord.fuel_type_id == FuelType.id)
        .join(Station, PriceRecord.station_id == Station.id)
        .filter(PriceRecord.batch_id == last_batch.id)
    )
    
    sql_str = str(qry.statement.compile(compile_kwargs={"literal_binds": True}))
    df = pd.read_sql_query(sql=sql_str, con=db.engine, parse_dates=['publish_date'])
    if df.empty:
        return None, None
 
    df['date_str']  = df['publish_date'].dt.strftime('%Y-%m-%d')
    df["date_str"]  = df["publish_date"].dt.strftime("%Y-%m-%d")
    df["week_str"]  = "Week " + df["publish_date"].dt.isocalendar().week.astype(str)
    df["month_str"] = df["publish_date"].dt.strftime("%Y-%m")

    df_f = df.copy()
    if fuel_type and fuel_type != "All Fuel Types":
        df_f = df_f[df_f["fuel_type"] == fuel_type]
    if location and location != "All Locations":
        df_f = df_f[df_f["location"] == location]
    if filter_date:
        df_f = df_f[df_f["date_str"] == filter_date]

    MAX_POINTS = 1000
    if len(df_f) > MAX_POINTS:
        types = df_f["fuel_type"].unique().tolist()
        per = max(1, MAX_POINTS // len(types))
        df_f = (
            df_f.groupby("fuel_type", group_keys=False)
                .apply(lambda g: g.sample(n=min(len(g), per), random_state=42))
        )
        if len(df_f) > MAX_POINTS:
            df_f = df_f.sample(n=MAX_POINTS, random_state=42)

    def build_chart(df_grp, label_col):
        labels = sorted(df_grp[label_col].unique().tolist())
        datasets = []
        for ft in df_grp["fuel_type"].unique():
            sub = df_grp[df_grp["fuel_type"] == ft]
            data = [
                round(sub[sub[label_col]==lbl]["price"].mean(), 2)
                    if not sub[sub[label_col]==lbl].empty else None
                for lbl in labels
            ]
            datasets.append({
                "label": ft,
                "data": data,
                "tension": 0.1
            })
        return {"labels": labels, "datasets": datasets}

    chart_data = {
        "daily":   build_chart(df_f, "date_str"),
        "weekly":  build_chart(df_f, "week_str"),
        "monthly": build_chart(df_f, "month_str"),
    }

    if not df_f.empty:
        avg_price  = df_f["price"].mean()
        vol        = df_f["price"].std() * 100
        min_price  = df_f["price"].min()
        max_price  = df_f["price"].max()
        metrics = {
            "avg_price":  f"${avg_price:.2f}",
            "volatility": f"{vol:.2f}%",
            "cheapest":   f"${min_price:.2f}",
            "expensive":  f"${max_price:.2f}"
        }

    return chart_data, metrics