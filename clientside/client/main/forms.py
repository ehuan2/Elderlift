from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import ValidationError



class AddressForm(FlaskForm):

    country = StringField('Country')
    city = StringField('City')
    address = StringField('Address')

    submit = SubmitField('Search')

    # validations for the input - cannot send address without city or country
    def validate_city(self, city):

        if city.data and not self.country.data:
            raise ValidationError("You need to specify a country!")

    def validate_address(self, address):

        if address.data and not self.city.data:
            raise ValidationError("You need to specify an address!")
