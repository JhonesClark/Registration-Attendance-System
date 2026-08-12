import unittest

from app import create_app
from app.forms import PersonForm
from app.models.person import Person


class StationRemovalTests(unittest.TestCase):
    def test_person_model_has_no_station_column(self):
        column_names = {column.name for column in Person.__table__.columns}
        self.assertNotIn('registration_station', column_names)

    def test_person_form_only_has_requested_fields(self):
        app = create_app()
        with app.test_request_context('/'):
            form = PersonForm()
            self.assertTrue(hasattr(form, 'name'))
            self.assertTrue(hasattr(form, 'category'))
            self.assertTrue(hasattr(form, 'person_type'))
            self.assertFalse(hasattr(form, 'registration_station'))


if __name__ == '__main__':
    unittest.main()
