from flask import Blueprint, redirect, render_template, url_for, request
from flask_login import login_required, current_user
from app.models import UploadBatch, FuelPrice
import pandas as pd

dashboard_bp = Blueprint(
    'dashboard',
    __name__,
    url_prefix='/dashboard',
    template_folder="../../templates/main"
)


@dashboard_bp.route('/')
@login_required
def dashboard_home():
    # Get filters from query parameters
    fuel_type = request.args.get('fuel_type')
    filter_date = request.args.get('date')
    location = request.args.get('location')

    # 1. Get the user's last upload batch
    last_batch = (
        UploadBatch.query
        .filter_by(user_id=current_user.id)
        .order_by(UploadBatch.uploaded_at.desc())
        .first()
    )
    # If no batch exists, just return the dashboard with empty data
    if not last_batch:
        empty = {'labels': [], 'datasets': []}
        chart_data = {'daily': empty, 'weekly': empty, 'monthly': empty}
        return render_template(
            'main/dashboard.html',
                               user=current_user,
                               chart_data=chart_data)

    # 2. load the all the data from that batch
    prices = FuelPrice.query.filter_by(batch_id=last_batch.id).all()
    df = pd.DataFrame([{
        'publish_date': p.publish_date,
        'fuel_type': p.trading_name,
        'price': p.product_price,
        'location': p.location
    } for p in prices])

    # 3. Convert to datetime and add grouping fields
    df['publish_date'] = pd.to_datetime(df['publish_date'])
    df['date_str'] = df['publish_date'].dt.strftime('%Y-%m-%d')
    df['week_str'] = 'Week ' + df['publish_date'].dt.isocalendar().week.astype(str)
    df['month_str'] = df['publish_date'].dt.strftime('%Y-%m')

    fuel_types = ['All Fuel Types'] + sorted(df['fuel_type'].unique().tolist())
    locations = ['All Locations'] + sorted(df['location'].unique().tolist())

    df_filtered = df.copy()
    if fuel_type != 'All Fuel Types':
        df_filtered = df_filtered[df_filtered['fuel_type'] == fuel_type]
    if location != 'All Locations':
        df_filtered = df_filtered[df_filtered['location'] == location]
    if filter_date:
        df_filtered = df_filtered[df_filtered['date_str'] == filter_date]

    MAX_POINTS = 1000
    if len(df_filtered) > MAX_POINTS:
        # 这里按 fuel_type 分层，各取等份样本，也可以直接 df_filtered.sample(n=MAX_POINTS)
        types = df_filtered['fuel_type'].unique().tolist()
        per_type = max(1, MAX_POINTS // len(types))
        df_filtered = (
            df_filtered
            .groupby('fuel_type', group_keys=False)
            .apply(lambda g: g.sample(n=min(len(g), per_type), random_state=42))
        )
        # 如果依然超过，再全局抽样到 MAX_POINTS
        if len(df_filtered) > MAX_POINTS:
            df_filtered = df_filtered.sample(n=MAX_POINTS, random_state=42)

    # —— 接下来照常构建 daily/weekly/monthly 三张图的数据 ——
    def build_chart(df_grouped, label_col):
        labels = sorted(df_grouped[label_col].unique().tolist())
        datasets = []
        for ft in df_grouped['fuel_type'].unique():
            sub = df_grouped[df_grouped['fuel_type'] == ft]
            data = [
                round(sub[sub[label_col] == lbl]['price'].mean(), 2)
                if not sub[sub[label_col] == lbl].empty else None
                for lbl in labels
            ]
            datasets.append({'label': ft, 'data': data, 'tension': 0.1})
        return {'labels': labels, 'datasets': datasets}

    chart_data = {
        'daily': build_chart(df_filtered, 'date_str'),
        'weekly': build_chart(df_filtered, 'week_str'),
        'monthly': build_chart(df_filtered, 'month_str'),
    }

    return render_template(
        'main/dashboard.html',
        user=current_user,
        chart_data=chart_data,
        fuel_types=fuel_types,
        locations=locations
    )


    # Build chart helper
    def build_chart(df_grouped, label_col):
        labels = sorted(df_grouped[label_col].unique().tolist())
        datasets = []
        for fuel in df_grouped['fuel_type'].unique():
            data = []
            sub = df_grouped[df_grouped['fuel_type'] == fuel]
            for lbl in labels:
                vals = sub[sub[label_col] == lbl]['price']
                data.append(round(vals.mean(), 2) if not vals.empty else None)
            datasets.append({
                'label': fuel,
                'data': data,
                'tension': 0.1
            })
        return {'labels': labels, 'datasets': datasets}
        # 4. Construct the data of the three charts of daily/weekly/monthly

    chart_data = {
        'daily': build_chart(df, 'date_str'),
        'weekly': build_chart(df, 'week_str'),
        'monthly': build_chart(df, 'month_str')
    }

    return render_template('main/dashboard.html', user=current_user, chart_data=chart_data)
