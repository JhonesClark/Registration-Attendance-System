from flask import render_template


def page_403(error):
    return render_template('errors/403.html'), 403


def page_404(error):
    return render_template('errors/404.html'), 404


def page_500(error):
    return render_template('errors/500.html'), 500


def register_error_handlers(app):
    app.register_error_handler(403, page_403)
    app.register_error_handler(404, page_404)
    app.register_error_handler(500, page_500)
