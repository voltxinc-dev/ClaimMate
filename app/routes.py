import psycopg2
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from config import Config

routes_bp = Blueprint('routes_bp', __name__)

def get_db_connection():
    return psycopg2.connect(
        dbname=Config.DB_NAME,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        host=Config.DB_HOST,
        port=Config.DB_PORT
    )

@routes_bp.route('/', methods=['GET', 'POST'])
def index():
    if 'user' not in session:
        return redirect(url_for('auth.login'))

    if 'edit_mode' not in session:
        session['edit_mode'] = True

    if request.method == 'POST' and 'toggle_mode' in request.form:
        pwd = request.form.get('switch_password')
        if pwd == 'private':
            session['edit_mode'] = not session.get('edit_mode')
            flash(f"Mode switched to {'Insert' if session['edit_mode'] else 'View'}.", "success")
        else:
            flash("Wrong mode switch password.", "danger")
        return redirect(url_for('routes_bp.index'))

    edit_mode = session.get('edit_mode')
    conn = get_db_connection()
    cur = conn.cursor()

    if edit_mode and request.method == 'POST' and 'toggle_mode' not in request.form:
        try:
            price = float(request.form.get('price_original', 0))
            cur.execute(
                "INSERT INTO exterior_car_parts (code, make_model, part_name, price_original, sourcer) VALUES (%s,%s,%s,%s,%s)",
                (request.form['code'], request.form['make_model'], request.form['part_name'], price, request.form['sourcer'])
            )
            conn.commit()
            flash("Part added successfully.", "success")
        except Exception as e:
            flash(f"Error inserting part: {e}", "danger")

    search = request.args.get('search', '').strip()
    if search:
        q = f"%{search}%"
        cur.execute(
            "SELECT id, code, make_model, part_name, price_original, sourcer FROM exterior_car_parts WHERE "
            "code ILIKE %s OR make_model ILIKE %s OR part_name ILIKE %s ORDER BY id DESC",
            (q, q, q)
        )
    else:
        cur.execute("SELECT id, code, make_model, part_name, price_original, sourcer FROM exterior_car_parts ORDER BY id DESC")

    parts = cur.fetchall()
    cur.close()
    conn.close()

    return render_template('index.html', parts=parts, username=session.get('user'), edit_mode=edit_mode)

@routes_bp.route('/edit/<int:part_id>', methods=['GET', 'POST'])
def edit_part(part_id):
    if 'user' not in session:
        return redirect(url_for('auth.login'))

    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        try:
            price = float(request.form.get('price_original', 0))
            cur.execute(
                "UPDATE exterior_car_parts SET code=%s, make_model=%s, part_name=%s, price_original=%s, sourcer=%s WHERE id=%s",
                (request.form['code'], request.form['make_model'], request.form['part_name'], price, request.form['sourcer'], part_id)
            )
            conn.commit()
            flash("Part updated.", "success")
            return redirect(url_for('routes_bp.index'))
        except Exception as e:
            flash(f"Update failed: {e}", "danger")

    cur.execute("SELECT * FROM exterior_car_parts WHERE id = %s", (part_id,))
    part = cur.fetchone()
    cur.close()
    conn.close()

    if not part:
        flash("Part not found.", "danger")
        return redirect(url_for('routes_bp.index'))

    return render_template('edit_part.html', part=part)

@routes_bp.route('/delete/<int:part_id>', methods=['POST'])
def delete_part(part_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM exterior_car_parts WHERE id = %s", (part_id,))
    conn.commit()
    cur.close()
    conn.close()
    flash("Part removed.", "info")
    return redirect(url_for('routes_bp.index'))

@routes_bp.route('/depreciation', methods=['GET', 'POST'])
def depreciation():
    if 'user' not in session:
        return redirect(url_for('auth.login'))

    result = error = None
    if request.method == 'POST':
        car = request.form.get('car_name')
        part = request.form.get('part_name')
        try:
            pct = float(request.form.get('depreciation_percentage'))
            if not (0 <= pct <= 100):
                raise ValueError
        except:
            error = "Enter a valid depreciation percentage (0–100)."
        else:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT price_original FROM exterior_car_parts WHERE make_model=%s AND part_name=%s", (car, part))
            row = cur.fetchone()
            cur.close()
            conn.close()

            if not row:
                error = "No matching part found."
            else:
                orig = row[0]
                cust = round(orig * pct / 100, 2)
                comp = round(orig - cust, 2)
                result = {
                    'price_original': orig,
                    'price_customer': cust,
                    'price_company': comp
                }

    return render_template('depreciation.html', result=result, error=error)
