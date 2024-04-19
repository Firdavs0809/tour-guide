from django.contrib.auth.password_validation import validate_password
from django.core.validators import RegexValidator
from django.db import transaction, IntegrityError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from tour.agency.models import Company, TempCompany, TourPackage, Category, Options, Hotel, City
from tour.user.models import User
from tour.agency.utils import check_username_exists

phone_regex = RegexValidator(regex=r'^\+?1?\d{9,12}$', message='invalid phone number')


class AgencyRegistrationSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True)
    password = serializers.CharField(max_length=30, required=True, write_only=True)
    name = serializers.CharField(max_length=56, required=True, )
    licence_number = serializers.CharField(required=True)
    licence = serializers.CharField(max_length=255, required=True)
    address = serializers.CharField(required=True, max_length=95, )
    tg_username = serializers.CharField(required=True, max_length=32, min_length=5)
    website = serializers.CharField(max_length=200, required=False)
    phone_number_2 = serializers.CharField(max_length=13, min_length=12, required=True, write_only=True,
                                           validators=[phone_regex])

    def validate(self, attrs):
        try:
            user = User.objects.get(phone_number=attrs.get('phone_number'))
            self.context['user'] = user
        except User.DoesNotExist:
            raise ValidationError({'success': False, 'detail': 'User phone_number should be confirmed first.'})

        if Company.objects.filter(admin=user).first():
            raise ValidationError({'success': False, 'detail': 'Company exist with this number.'})

        validate_password(attrs.get('password'))
        return attrs

    def validate_address(self, address):
        return address

    def validate_licence_number(self, licence_number):
        if len(licence_number) > 12:
            message = _("Licence number is not more than 12 characters long.")
            raise ValidationError({'detail': message})
        return licence_number

    def validate_tg_username(self, tg_username):
        if not check_username_exists(tg_username.replace('@', '')):
            message = _("Telegram username does not exist")
            raise ValidationError({'detail': message})
        return tg_username

    def save_temp(self, **kwargs):
        tmp = self.getTempObject()
        if not tmp:
            try:
                tmp = TempCompany.objects.create(
                    name=self.validated_data.get('name', None),
                    phone_number="+" + self.validated_data.get('phone_number', None).replace('+', ''),
                    # phone_number=self.context.get('request').user.phone_number,
                    phone_number_2=self.validated_data.get('phone_number_2', None),
                    licence_number=self.validated_data.get('licence_number', None),
                    licence=self.validated_data.get('licence', None),
                    address=self.validated_data.get('address', None),
                    tg_username=self.validated_data.get('tg_username', None),
                    website=self.validated_data.get('website', "No website"),
                )
            except IntegrityError as error:
                error_message = _(
                    f"{str(error).split('(')[1].replace(')=', '')} already registered for another company.")
                raise ValidationError({'detail': error_message})
        return tmp

    def save(self, **kwargs):
        self.save_temp(**kwargs)

        tmp = TempCompany.objects.filter(phone_number="+" + self.validated_data.get('phone_number').replace('+', ''),
                                         is_verified=False).first()
        if not tmp:
            raise ValidationError(
                {'detail': _('Phone number is invalid. Please try the phone number used in registration!')})
        with transaction.atomic():
            try:
                agency = Company.objects.create(
                    admin=self.context.get('user'),
                    phone_number_2=tmp.phone_number_2,
                    licence_number=tmp.licence_number,
                    licence=tmp.licence,
                    tg_username=tmp.tg_username,
                    website=tmp.website,
                    address=tmp.address,
                    name=tmp.name
                )

            except IntegrityError as e:
                if "UNIQUE constraint" in e.args:
                    error_message = "Please take a look at the Naming of the company that company already exists."
                else:
                    error_message = 'Error occurred during creation please contact support!'
                raise ValidationError(error_message)
            except User.DoesNotExist:
                error_message = 'Company admin account not activated successfully!'
                raise ValidationError(error_message)

            # agency.is_waiting = True
            # agency.save()
            tmp.is_verified = True
            tmp.save()
            return agency
        return None

    def getTempObject(self, ):
        try:
            temp = TempCompany.objects.get(phone_number="+" + self.validated_data.get('phone_number').replace('+', ''))
            # temp = TempCompany.objects.get(phone_number=self.context.get('request'))
            try:
                temp.name = self.validated_data.get("name")
                temp.phone_number_2 = self.validated_data.get("phone_number_2")
                temp.licence_number = self.validated_data.get("licence_number")
                temp.licence = self.validated_data.get("licence")
                temp.address = self.validated_data.get("address")
                temp.tg_username = self.validated_data.get("tg_username")
                temp.website = self.validated_data.get("website", "No Website")
                temp.is_verified = False
                temp.save()
                return temp
            except IntegrityError as error:
                if "UNIQUE constraint" in error:
                    error_message = _("The Unique constraint failed!")
                    raise ValidationError({'detail': error_message})
        except TempCompany.DoesNotExist:
            return False


class AgencyRegistrationActivationSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    code = serializers.CharField()

    password = serializers.CharField(required=True, write_only=True, min_length=4, max_length=30, )
    grant_type = serializers.CharField(required=True, write_only=True)
    client_id = serializers.CharField(min_length=10, required=True, write_only=True)
    client_secret = serializers.CharField(required=True, write_only=True)

    def save(self, **kwargs):
        tmp = TempCompany.objects.filter(phone_number="+" + self.validated_data.get('phone_number').replace('+', ''),
                                         is_verified=False).first()
        if not tmp:
            raise ValidationError(
                {'detail': _('Phone number is invalid. Please try the phone number used in registration!')})
        with transaction.atomic():
            try:
                agency = Company.objects.create(
                    admin=User.objects.get(phone_number=tmp.phone_number),
                    phone_number_2=tmp.phone_number_2,
                    licence_number=tmp.licence_number,
                    licence=tmp.licence,
                    tg_username=tmp.tg_username,
                    website=tmp.website,
                    address=tmp.address,
                    name=tmp.name
                )

            except IntegrityError as e:
                if "UNIQUE constraint" in e.args:
                    error_message = "Please take a look at the Naming of the company that company already exists."
                else:
                    error_message = 'Error occurred during creation please contact support!'
                raise ValidationError(error_message)
            except User.DoesNotExist:
                error_message = 'Company admin account not activated successfully!'
                raise ValidationError(error_message)

            # agency.is_waiting = True
            # agency.save()
            tmp.is_verified = True
            tmp.save()
            return agency
        return None


class CompanyListSerializer(serializers.ModelSerializer):
    phone_number = serializers.SerializerMethodField()

    def get_phone_number(self, obj):
        return obj.admin.phone_number

    class Meta:
        model = Company
        fields = ['id', 'name', 'website', 'address', 'phone_number', 'licence_number']
        read_only_fields = fields


class TourPackageCreateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=True, max_length=48)
    city_from = serializers.IntegerField(required=True)
    city_to = serializers.IntegerField(required=True)
    activities = serializers.ListField(required=False)
    destinations = serializers.ListField(required=False)
    category = serializers.ListField(required=False)
    hotels = serializers.ListField(required=True)
    images = serializers.ListField(required=True)
    # airport_from = serializers.CharField(required=True)
    # airport_to = serializers.CharField(required=False)
    options = serializers.ListField(required=True)

    class Meta:
        model = TourPackage
        exclude = ['id', 'is_expired', 'is_featured', 'image', 'language', 'agency']

    def validate(self, attrs):
        message = None
        if attrs.get('ending_date') <= attrs.get("starting_date"):
            message = _("Invalid date interval for tour. Please check the starting and ending date you entered.")
        if message:
            raise ValidationError({'success': False, 'message': message})
        return attrs

    def validate_title(self, title):
        message = None
        if len(title) < 4:
            message = _("Invalid title. Consider giving a descriptive name for the Tour.")
        if message:
            raise ValidationError({'success': False, 'message': message})
        return title

    def validate_airport_from(self, airport_from):
        message = None
        if len(airport_from) < 5:
            message = _("Invalid Airport. Consider giving a descriptive Airport name for the Tour.")
        if message:
            raise ValidationError({'success': False, 'message': message})
        return airport_from

    def validate_airport_to(self, airport_to):
        message = None
        if len(airport_to) < 5:
            message = _("Invalid Airport. Consider giving a descriptive Airport name for the Tour.")
        if message:
            raise ValidationError({'success': False, 'message': message})
        return airport_to

    def validate_starting_date(self, starting_date):
        if starting_date <= timezone.now().date():
            raise ValidationError({'success': False, 'message': _(
                "Invalid starting date for tour. Please check the date you entered.")})
        return starting_date

    def validate_ending_date(self, ending_date):
        if ending_date <= timezone.now().date():
            raise ValidationError({'success': False, 'message': _(
                "Invalid ending date for tour. Please check the date you entered.")})
        return ending_date

    def validate_city_from(self, city_from):
        if not City.objects.filter(id=city_from).exists():
            raise ValidationError({'success': False, 'message': _(
                "Invalid city_from for tour. Please select valid city.")})
        return city_from

    def validate_city_to(self, city_to):
        if not City.objects.filter(id=city_to).exists():
            raise ValidationError({'success': False, 'message': _(
                "Invalid city_to for tour. Please select valid city.")})
        return city_to

    def validate_price(self, price):
        if price <= 0:
            raise ValidationError({'success': False, 'message': _(
                "Invalid price tag. Price should be non negative number.")})
        if price >= 10000000:
            raise ValidationError({'success': False, 'message': _(
                "Invalid price tag. Please consider entering realistic price.")})
        return price

    def create(self, validated_data):

        package = TourPackage.objects.filter(title=validated_data.get('title'), )
        if package.exists():
            raise ValidationError({'success': False, 'message': _(
                "Tour already registered. If you want to edit it . Go to the edit page.")})

        admin = self.context.get('admin')
        with transaction.atomic():
            package = TourPackage.objects.create(
                agency=admin.agency,
                title=validated_data.get('title'),
                description=validated_data.get('description'),
                starting_date=validated_data.get('starting_date'),
                ending_date=validated_data.get('ending_date'),
                price=validated_data.get('price'),
                # airport_from=validated_data.get('airport_from', None),
                # airport_to=validated_data.get('airport_to', None),
                city_from_id=validated_data.get('city_from'),
                city_to_id=validated_data.get('city_to')
            )

            # category = validated_data.get('category')[0].split(',')
            options = validated_data.get('options')[0].replace('[', '').replace(']', '').split(',')
            hotels = validated_data.get('hotels')[0].replace('[', '').replace(']', '').split(',')
            images = validated_data.get('images')[0].replace('[', '').replace(']', '').split(',')

            for image in images:
                allowed_image_format = ['jpg', 'jpeg', 'png', 'avif', 'gif']
                if image.split('.')[-1] not in allowed_image_format:
                    raise ValidationError(
                        {'success': False,
                         'message': _(f"Image extension not allowed.Allowec exts:{allowed_image_format}'")})
                try:
                    package.images.append(image)
                except AttributeError:
                    package.images = [image]
                    package.image = image

            # for each_category in category:
            #     try:
            #         obj = Category.objects.get(id=each_category)
            #     except Exception as e:
            #         raise ValidationError(
            #             {'success': False, 'message': _(f"Category with id:{each_category} does not exist.")})
            #     finally:
            #         package.category.add(obj)

            for option in options:
                try:
                    obj = Options.objects.get(id=option)
                except Exception as e:
                    raise ValidationError(
                        {'success': False, 'message': _(f"Option with id:{option} does not exist.")})
                finally:
                    package.options.add(obj)

            for hotel in hotels:
                try:
                    obj = Hotel.objects.get(id=hotel)
                except Exception as e:
                    raise ValidationError(
                        {'success': False, 'message': _(f"HOTEL with id:{hotel} does not exist.")})
                finally:
                    package.hotels.add(obj)

            package.save()
        self.validated_data['message'] = _('Your package created successfully!')
        return package

    def update(self, instance, validated_data):
        package = instance

        package.title = validated_data.get('title', package.title)
        package.starting_date = validated_data.get('starting_date', package.starting_date)
        package.ending_date = validated_data.get('ending_date', package.ending_date)
        package.description = validated_data.get('description', package.description)
        # package.airport_from = validated_data.get('airport_from', package.airport_from)
        # package.airport_to = validated_data.get('airport_to', package.airport_to)
        package.price = validated_data.get('price', package.price)
        package.city_from_id = validated_data.get('city_from', package.city_from_id)
        package.city_to_id = validated_data.get('city_to', package.city_to_id)

        # category = validated_data.get('category')[0].split(',')
        options, hotels, images = validated_data.get('options')[
            0].split(','), validated_data.get('hotels')[0].split(','), validated_data.get('images')[0].split(',')

        clone_images = package.images
        if clone_images:
            for uploaded_image in clone_images:
                if uploaded_image not in images:
                    package.images.remove(uploaded_image)

        for image in images:
            allowed_image_format = ['jpg', 'jpeg', 'png', 'avif', 'gif']
            if image.split('.')[-1] not in allowed_image_format:
                raise ValidationError(
                    {'success': False,
                     'message': _(f"Image extension not allowed.Allowec exts:{allowed_image_format}'")})
            try:
                package.images.append(image)
            except AttributeError:
                package.images = [image]
                package.image = image

        # for each_category in package.category.all():
        #     if each_category.id not in category:
        #         package.category.remove(each_category)
        #
        # for each_category in category:
        #     try:
        #         obj = Category.objects.get(id=each_category)
        #     except Exception as e:
        #         raise ValidationError(
        #             {'success': False, 'message': _(f"Category with id:{each_category} does not exist.")})
        #     finally:
        #         if each_category not in package.category.all():
        #             package.category.add(obj)

        for option in package.options.all():
            if option.id not in options:
                package.options.remove(option)

        for option in options:
            try:
                obj = Options.objects.get(id=option)
            except Exception as e:
                raise ValidationError(
                    {'success': False, 'message': _(f"Option with id:{option} does not exist.")})
            finally:
                if option not in package.options.all():
                    package.options.add(obj)

        for hotel in package.hotels.all():
            if hotel.id not in hotels:
                package.hotels.remove(hotel)

        for hotel in hotels:
            try:
                obj = Hotel.objects.get(id=hotel)
            except Exception as e:
                raise ValidationError(
                    {'success': False, 'message': _(f"HOTEL with id:{hotel} does not exist.")})
            finally:
                if hotel not in package.hotels.all():
                    package.hotels.add(obj)

        package.save()
        self.validated_data['message'] = _('Changes saved successfully!')
        return package

    def to_representation(self, instance):
        data = {
            'success': 'ok',
            'message': _(self.validated_data.get('message', "Something went wrong Please contact support!"))
        }
        return data
