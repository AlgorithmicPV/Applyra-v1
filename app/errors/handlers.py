"""Custom HTTP error handlers for the Flask application."""

from flask import render_template


def register_error_handlers(app):
    """
    Register custom HTTP error handlers for the Flask application.

    Args:
        app (Flask): The Flask application instance.

    Returns:
        None: The function registers error handlers directly with the app.
    """

    @app.errorhandler(400)
    def bad_request(_error):
        """
        Handle a 400 Bad Request error.

        Args:
            _error (Exception): The error raised by Flask.

        Returns:
            tuple: The rendered error page and HTTP status code 400.
        """
        return render_template(
            "errors/error.html",
            error_code=400,
            error_title="Bad Request",
            error_message="The request could not be processed.",
        ), 400

    @app.errorhandler(403)
    def forbidden(_error):
        """
        Handle a 403 Forbidden error.

        Args:
            _error (Exception): The error raised by Flask.

        Returns:
            tuple: The rendered error page and HTTP status code 403.
        """
        return render_template(
            "errors/error.html",
            error_code=403,
            error_title="Access Denied",
            error_message="You do not have permission to access this page.",
        ), 403

    @app.errorhandler(404)
    def not_found(_error):
        """
        Handle a 404 Page Not Found error.

        Args:
            _error (Exception): The error raised by Flask.

        Returns:
            tuple: The rendered error page and HTTP status code 404.
        """
        return render_template(
            "errors/error.html",
            error_code=404,
            error_title="Page Not Found",
            error_message="The page you are looking for does not exist.",
        ), 404

    @app.errorhandler(405)
    def method_not_allowed(_error):
        """
        Handle a 405 Method Not Allowed error.

        Args:
            _error (Exception): The error raised by Flask.

        Returns:
            tuple: The rendered error page and HTTP status code 405.
        """
        return render_template(
            "errors/error.html",
            error_code=405,
            error_title="Method Not Allowed",
            error_message="This request method is not supported.",
        ), 405

    @app.errorhandler(500)
    def internal_server_error(_error):
        """
        Handle a 500 Internal Server Error.

        Args:
            _error (Exception): The error raised by Flask.

        Returns:
            tuple: The rendered error page and HTTP status code 500.
        """
        return render_template(
            "errors/error.html",
            error_code=500,
            error_title="Something Went Wrong",
            error_message="An unexpected error occurred.",
        ), 500
