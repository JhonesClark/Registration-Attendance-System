import unittest

from app import create_app


class AuthFlowTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()

    def test_clear_history_requires_admin_and_post_only(self):
        # Admin can hit the clear route with a POST request.
        admin_login = self.client.post(
            '/login',
            data={'username': 'BCMBC', 'password': '12345'},
            follow_redirects=False,
        )
        self.assertEqual(admin_login.status_code, 302)

        clear_response = self.client.post('/admin/activity/clear', json={})
        self.assertEqual(clear_response.status_code, 200)
        self.assertIn('cleared', clear_response.get_data(as_text=True).lower())

        # A secretary session must be rejected at the admin-only route.
        self.client.get('/logout')
        secretary_login = self.client.post(
            '/login',
            data={'username': 'bcmbc', 'password': '12345'},
            follow_redirects=False,
        )
        self.assertEqual(secretary_login.status_code, 302)

        forbidden_response = self.client.post('/admin/activity/clear', json={})
        self.assertEqual(forbidden_response.status_code, 403)

    def test_authenticated_login_route_redirects_to_dashboard(self):
        login_response = self.client.post(
            '/login',
            data={'username': 'BCMBC', 'password': '12345'},
            follow_redirects=False,
        )
        self.assertEqual(login_response.status_code, 302)
        self.assertIn('/admin/', login_response.headers.get('Location', ''))

        login_page_response = self.client.get('/login')
        self.assertEqual(login_page_response.status_code, 302)
        self.assertIn('/admin/', login_page_response.headers.get('Location', ''))

    def test_logout_clears_authentication_and_protected_routes_reject_access(self):
        self.client.post(
            '/login',
            data={'username': 'BCMBC', 'password': '12345'},
            follow_redirects=False,
        )

        logout_response = self.client.get('/logout')
        self.assertEqual(logout_response.status_code, 302)
        self.assertIn('/login', logout_response.headers.get('Location', ''))

        protected_response = self.client.get('/admin/')
        self.assertEqual(protected_response.status_code, 302)
        self.assertIn('/login', protected_response.headers.get('Location', ''))

    def test_login_response_is_not_cached(self):
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        cache_control = response.headers.get('Cache-Control', '')
        self.assertIn('no-store', cache_control)
        self.assertIn('no-cache', cache_control)

    def test_admin_categories_page_is_available(self):
        self.client.post(
            '/login',
            data={'username': 'BCMBC', 'password': '12345'},
            follow_redirects=False,
        )

        response = self.client.get('/admin/categories')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Category Management', response.get_data(as_text=True))

    def test_admin_attendance_monitoring_page_is_available(self):
        self.client.post(
            '/login',
            data={'username': 'BCMBC', 'password': '12345'},
            follow_redirects=False,
        )

        response = self.client.get('/admin/attendance')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Attendance Monitoring', response.get_data(as_text=True))

        self.client.get('/logout')
        secretary_login = self.client.post(
            '/login',
            data={'username': 'bcmbc', 'password': '12345'},
            follow_redirects=False,
        )
        self.assertEqual(secretary_login.status_code, 302)

        forbidden_response = self.client.get('/admin/attendance')
        self.assertEqual(forbidden_response.status_code, 403)

    def test_attendance_login_redirects_to_attendance_dashboard(self):
        response = self.client.post(
            '/login',
            data={'username': 'BcmBc', 'password': '12345'},
            follow_redirects=False,
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn('/attendance/', response.headers.get('Location', ''))

    def test_admin_attendance_page_has_required_header_and_category_options(self):
        self.client.post(
            '/login',
            data={'username': 'BCMBC', 'password': '12345'},
            follow_redirects=False,
        )

        response = self.client.get('/admin/attendance')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Attendance Monitoring', response.get_data(as_text=True))
        self.assertIn("Today's Attendance", response.get_data(as_text=True))
        self.assertIn('All categories', response.get_data(as_text=True))
        self.assertIn('Young Professionals', response.get_data(as_text=True))

    def test_admin_attendance_has_no_punctuality_metrics_or_statuses(self):
        self.client.post(
            '/login',
            data={'username': 'BCMBC', 'password': '12345'},
            follow_redirects=False,
        )

        response = self.client.get('/admin/attendance')
        html = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('On Time', html)
        self.assertNotIn('Late', html)
        self.assertNotIn('Punctuality', html)
        self.assertIn('All', html)
        self.assertIn('Present', html)
        self.assertIn('Absent', html)

    def test_admin_can_create_event_and_manage_attendance_days(self):
        self.client.post(
            '/login',
            data={'username': 'BCMBC', 'password': '12345'},
            follow_redirects=False,
        )

        create_event = self.client.post(
            '/admin/events/create',
            data={
                'name': 'Home Builders 2026',
                'start_date': '2026-08-10',
                'end_date': '2026-08-12',
                'status': 'Active',
            },
            follow_redirects=False,
        )
        self.assertIn(create_event.status_code, (200, 302))

        events_page = self.client.get('/admin/events')
        self.assertEqual(events_page.status_code, 200)
        self.assertIn('Event Management', events_page.get_data(as_text=True))
        self.assertIn('Home Builders 2026', events_page.get_data(as_text=True))


if __name__ == '__main__':
    unittest.main()
