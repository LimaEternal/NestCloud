from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    send_from_directory,
    send_file,
    abort,
)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.exceptions import RequestEntityTooLarge
from flask_login import login_user, logout_user, login_required, current_user
from nestcloud import db, app
from nestcloud.models import User, File
from forms import UploadForm
import os
from utils import save_file


@app.route("/")
def root():
    return redirect("/home")


@app.route("/home")
def home():
    if current_user.is_authenticated:
        user_files = (
            File.query.filter_by(user_id=current_user.id)
            .order_by(File.upload_time.desc())
            .all()
        )
        form = UploadForm()  # Создаём форму
        return render_template(
            "home.html", files=user_files, form=form
        )  # Передаём form
    return render_template("home.html")


@app.route("/upload", methods=["POST"])
@login_required
def upload_file():
    print("\n" + "=" * 50)
    print("🔍 ЗАГРУЗКА ФАЙЛА ЧЕРЕЗ ФОРМУ")

    form = UploadForm()
    if not form.validate_on_submit():
        print("❌ Валидация формы провалена")
        for error in form.file.errors:
            print(f"   • {error}")
            flash(error, "danger")
        return redirect(url_for("home"))

    file = form.file.data
    print(f"📥 Получен файл: {file.filename}")

    try:
        saved_data = save_file(file, current_user.id)
        print(f"   → Данные для БД: preview_path = {saved_data.get('preview_relpath')}")

        new_file = File(
            filename=saved_data["original_filename"],
            stored_filename=saved_data["stored_filename"],
            user_id=current_user.id,
            file_size=saved_data["human_size"],
            upload_time=saved_data["upload_time"],
            preview_path=saved_data["preview_relpath"],
        )
        db.session.add(new_file)
        db.session.commit()

        print(
            f"✅ Файл успешно загружен и сохранён в БД (preview_path: {new_file.preview_path})"
        )
        flash(f"Файл '{saved_data['original_filename']}' загружен!", "success")

    except Exception as e:
        print(f"🔥 ОШИБКА: {str(e)}")
        import traceback

        traceback.print_exc()
        flash("Ошибка при загрузке файла", "danger")

    print("=" * 50 + "\n")
    return redirect(url_for("home"))


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        login = request.form.get("login")
        password = request.form.get("password")
        if not login or not password:
            flash("Пожалуйста, заполните все поля!")
            return render_template("register.html")
        else:
            user = User.query.filter_by(login=login).first()
            if user:
                flash("Пользователь с данным логином уже существует!")
                return render_template("register.html")
            else:
                print(login, password)
                hash_pwd = generate_password_hash(password)
                new_user = User(login=login, password=hash_pwd)
                db.session.add(new_user)
                db.session.commit()
        # === СОЗДАЁМ ПАПКУ ДЛЯ ПОЛЬЗОВАТЕЛЯ ===
        try:
            user_folder = os.path.join(app.config["UPLOAD_FOLDER"], f"{new_user.id}")
            os.makedirs(
                user_folder, exist_ok=True
            )  # exist_ok=True предотвратит ошибку, если папка уже есть
            print(f"Папка создана: {user_folder}")
        except Exception as e:
            print(f"Ошибка создания папки: {str(e)}")

        return redirect(url_for("login_page"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login_page():
    if request.method == "POST":
        login = request.form.get("login")
        password = request.form.get("password")

        if not login or not password:
            flash("Пожалуйста, заполните все поля!")
            return render_template("login.html")
        else:
            user = User.query.filter_by(login=login).first()
            if user and check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for("home"))
            else:
                flash("Неверный логин или пароль!")

    return render_template("login.html")


@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/preview/<int:file_id>")
@login_required
def preview_file(file_id):
    file_record = File.query.get_or_404(file_id)
    if file_record.user_id != current_user.id:
        abort(403)

    if not file_record.preview_path:
        abort(404)

    # Если preview_path начинается с "file_icons/", это статическая иконка
    if file_record.preview_path.startswith("file_icons/"):
        return send_from_directory("static", file_record.preview_path)

    # Иначе это сгенерированное превью в папке пользователя
    user_folder = os.path.join(app.config["UPLOAD_FOLDER"], f"{file_record.user_id}")
    preview_full_path = os.path.join(user_folder, file_record.preview_path)

    if not os.path.exists(preview_full_path):
        abort(404)

    directory, filename = os.path.split(preview_full_path)
    return send_from_directory(directory, filename)


@app.route("/download/<int:file_id>")
@login_required
def download_file(file_id):
    """Скачивает файл с оригинальным именем"""
    file_record = File.query.get_or_404(file_id)

    # Проверяем, что файл принадлежит текущему пользователю
    if file_record.user_id != current_user.id:
        abort(403)

    try:
        user_folder = os.path.join(
            app.config["UPLOAD_FOLDER"], f"{file_record.user_id}"
        )
        file_path = os.path.join(user_folder, file_record.stored_filename)

        if not os.path.exists(file_path):
            flash("Файл не найден на сервере", "danger")
            return redirect(url_for("home"))

        # Отправляем файл с оригинальным именем
        return send_file(
            file_path,
            as_attachment=True,
            download_name=file_record.filename,
            mimetype="application/octet-stream",
        )

    except Exception as e:
        print(f"🔥 ОШИБКА при скачивании файла: {str(e)}")
        import traceback

        traceback.print_exc()
        flash("Ошибка при скачивании файла", "danger")
        return redirect(url_for("home"))


@app.route("/delete/<int:file_id>", methods=["POST"])
@login_required
def delete_file(file_id):
    """Удаляет файл, его превью и запись из БД"""
    file_record = File.query.get_or_404(file_id)

    # Проверяем, что файл принадлежит текущему пользователю
    if file_record.user_id != current_user.id:
        abort(403)

    try:
        user_folder = os.path.join(
            app.config["UPLOAD_FOLDER"], f"{file_record.user_id}"
        )

        # Удаляем основной файл
        file_path = os.path.join(user_folder, file_record.stored_filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"✅ Файл удалён: {file_path}")

        # Удаляем превью, если оно есть
        if file_record.preview_path:
            preview_full_path = os.path.join(user_folder, file_record.preview_path)
            if os.path.exists(preview_full_path):
                os.remove(preview_full_path)
                print(f"✅ Превью удалено: {preview_full_path}")

        # Удаляем запись из БД
        filename = file_record.filename
        db.session.delete(file_record)
        db.session.commit()

        flash(f"Файл '{filename}' успешно удалён", "success")
        print(f"✅ Запись из БД удалена для файла: {filename}")

    except Exception as e:
        db.session.rollback()
        print(f"🔥 ОШИБКА при удалении файла: {str(e)}")
        import traceback

        traceback.print_exc()
        flash("Ошибка при удалении файла", "danger")

    return redirect(url_for("home"))


@app.route("/rename/<int:file_id>", methods=["POST"])
@login_required
def rename_file(file_id):
    """Переименовывает файл (изменяет только имя в БД, физический файл не переименовывается)"""
    file_record = File.query.get_or_404(file_id)

    # Проверяем, что файл принадлежит текущему пользователю
    if file_record.user_id != current_user.id:
        abort(403)

    new_filename = request.form.get("new_filename", "").strip()

    if not new_filename:
        flash("Имя файла не может быть пустым", "danger")
        return redirect(url_for("home"))

    # Проверяем, что имя файла не содержит опасных символов
    if any(
        char in new_filename
        for char in ["/", "\\", "..", "<", ">", ":", '"', "|", "?", "*"]
    ):
        flash("Имя файла содержит недопустимые символы", "danger")
        return redirect(url_for("home"))

    # Получаем расширение оригинального файла
    old_extension = ""
    if "." in file_record.filename:
        old_extension = "." + file_record.filename.rsplit(".", 1)[1]

    # Удаляем расширение из введенного имени (если есть)
    if "." in new_filename:
        new_filename = new_filename.rsplit(".", 1)[0]

    # Всегда добавляем оригинальное расширение
    if old_extension:
        new_filename = new_filename + old_extension

    try:
        old_filename = file_record.filename
        file_record.filename = new_filename
        db.session.commit()

        flash("Имя файла изменено", "success")
        print(f"✅ Файл переименован: {old_filename} -> {new_filename}")

    except Exception as e:
        db.session.rollback()
        print(f"🔥 ОШИБКА при переименовании файла: {str(e)}")
        import traceback

        traceback.print_exc()
        flash("Ошибка при переименовании файла", "danger")

    return redirect(url_for("home"))


@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(e):
    flash("Файл слишком большой! Максимальный размер — 512 МБ.", "danger")
    return redirect(url_for("home"))


@app.route("/about")
def about_page():
    return render_template("about.html")
