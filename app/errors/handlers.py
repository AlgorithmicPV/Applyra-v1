from flask import render_template


def register_error_handlers(app):

    @app.errorhandler(400)
    def bad_request(error):
        return render_template(
            "errors/error.html",
            error_code=400,
            error_title="Bad Request",
            error_message="The request could not be processed.",
        ), 400

    @app.errorhandler(403)
    def forbidden(error):
        return render_template(
            "errors/error.html",
            error_code=403,
            error_title="Access Denied",
            error_message="You do not have permission to access this page.",
        ), 403

    @app.errorhandler(404)
    def not_found(error):
        return render_template(
            "errors/error.html",
            error_code=404,
            error_title="Page Not Found",
            error_message="The page you are looking for does not exist.",
        ), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return render_template(
            "errors/error.html",
            error_code=405,
            error_title="Method Not Allowed",
            error_message="This request method is not supported.",
        ), 405

    @app.errorhandler(500)
    def internal_server_error(error):
        return render_template(
            "errors/error.html",
            error_code=500,
            error_title="Something Went Wrong",
            error_message="An unexpected error occurred.",
        ), 500
