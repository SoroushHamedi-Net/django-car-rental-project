class VisitCountCookieMiddleware:
    """
    میدل‌ور ثبت و به‌روزرسانی تعداد بازدیدهای کاربر در کوکی مرورگر (visit_count).
    """
    COOKIE_NAME = 'visit_count'
    COOKIE_MAX_AGE = 30 * 24 * 60 * 60  # 30 روز

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        raw_count = request.COOKIES.get(self.COOKIE_NAME, '0')
        try:
            current_count = max(int(raw_count), 0)
        except (TypeError, ValueError):
            current_count = 0

        is_trackable_request = (
            request.method == 'GET'
            and not request.path.startswith(('/static/', '/media/', '/admin/'))
        )
        next_count = current_count + 1 if is_trackable_request else current_count
        request.visit_count = next_count

        response = self.get_response(request)

        content_type = response.get('Content-Type', '')
        if is_trackable_request and response.status_code == 200 and 'text/html' in content_type:
            response.set_cookie(
                self.COOKIE_NAME,
                str(next_count),
                max_age=self.COOKIE_MAX_AGE,
                samesite='Lax',
            )

        return response
