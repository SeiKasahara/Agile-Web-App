# app/routes/share.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import UploadBatch, User, DataShare
from app import db

share_bp = Blueprint('share', __name__, url_prefix='/share')

@share_bp.route('/', methods=['GET', 'POST'])
@login_required
def share_data():
    batches = (UploadBatch.query
               .filter_by(user_id=current_user.id)
               .order_by(UploadBatch.uploaded_at.desc())
               .all())
    users = User.query.filter(User.id != current_user.id).all()

    if request.method == 'POST':
        batch_id     = int(request.form['batch_id'])
        selected_ids = request.form.getlist('shared_to')

        DataShare.query.filter_by(owner_id=current_user.id, batch_id=batch_id).delete()

        for uid in selected_ids:
            share = DataShare(
                owner_id     = current_user.id,
                batch_id     = batch_id,
                shared_to_id = int(uid)
            )
            db.session.add(share)

        db.session.commit()
        flash("Sharing settings updated", "success")
        return redirect(url_for('share.share_data'))

    shares_map = {}
    for b in batches:
        shares_map[b.id] = [ ds.shared_to_id for ds in b.shares ]

    return render_template(
        'main/share_data.html',
        batches=batches,
        users=users,
        shares_map=shares_map
    )
