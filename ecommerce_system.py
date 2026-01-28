"""
نظام متكامل لإدارة المستخدمين والمنتجات والطلبات
ملف واحد (Single-file) - Python 3
الوظائف: OOP, Validation, Exceptions, Managers, Console Menu, صلاحيات (Admin/Employee/Customer)
تعليقات باللغة العربية لتسهيل القراءة.
"""

from typing import Dict, List, Tuple, Optional
import re
import sys
import json
import os

# =========================
# Exceptions مخصصة
# =========================
class ValidationError(Exception):
    """خطأ في التحقق من صحة البيانات"""
    pass

class AuthenticationError(Exception):
    """خطأ في المصادقة"""
    pass

class AuthorizationError(Exception):
    """خطأ في الصلاحيات"""
    pass

class NotFoundError(Exception):
    """عنصر غير موجود"""
    pass

# =========================
# Validators: قواعد التحقق
# =========================
class Validators:
    PHONE_PREFIXES = ('71', '73', '77', '78')

    @staticmethod
    def validate_username(username: str, existing_usernames: List[str] = None) -> bool:
        if not username or not username.strip():
            raise ValidationError("Username is required")
        # يسمح بالأحرف والأرقام وال underscore فقط
        if not re.match(r'^[A-Za-z0-9_]+$', username):
            raise ValidationError("Username must contain letters, digits or underscore only")
        if existing_usernames and username in existing_usernames:
            raise ValidationError("The username is found")
        return True

    @staticmethod
    def validate_password(password: str, min_len: int = 8) -> bool:
        if not password:
            raise ValidationError("Password is required")
        if len(password) < min_len:
            raise ValidationError(f"Password must be at least {min_len} characters")
        if not re.search(r'\d', password):
            raise ValidationError("Password must include at least one digit")
        if not re.search(r'[A-Za-z]', password):
            raise ValidationError("Password must include at least one letter")
        if not re.search(r'[^\w\s]', password):
            raise ValidationError("Password must include at least one special character")
        return True

    @staticmethod
    def validate_phonenumber(phonenumber: str) -> bool:
        if not phonenumber:
            raise ValidationError("Phone number is required")
        if not phonenumber.isdigit():
            raise ValidationError("Phone number must contain digits only")
        if len(phonenumber) != 9:
            raise ValidationError("Phone number must be 9 digits")
        if not phonenumber.startswith(Validators.PHONE_PREFIXES):
            raise ValidationError(f"Phone number must start with one of: {', '.join(Validators.PHONE_PREFIXES)}")
        return True

    @staticmethod
    def validate_usertype(usertype: str) -> bool:
        if not usertype:
            raise ValidationError("User type is required")
        if usertype.lower() not in ('admin', 'employee', 'customer'):
            raise ValidationError("User type must be one of: admin, employee, customer")
        return True

    @staticmethod
    def validate_gender(gender: str) -> bool:
        if not gender:
            raise ValidationError("Gender is required")
        if gender.lower() not in ('m', 'f', 'male', 'female', 'other'):
            raise ValidationError("Gender value seems invalid")
        return True

    @staticmethod
    def validate_product_id(pid) -> bool:
        if pid is None:
            raise ValidationError("Product ID is required")
        return True

    @staticmethod
    def validate_product_name(name: str) -> bool:
        if not name or not name.strip():
            raise ValidationError("Product name is required")
        return True

    @staticmethod
    def validate_price(price) -> bool:
        try:
            p = float(price)
        except Exception:
            raise ValidationError("Product price must be a number")
        if p < 0:
            raise ValidationError("Product price must be non-negative")
        return True

    @staticmethod
    def validate_quantity(qty) -> bool:
        if not isinstance(qty, int):
            raise ValidationError("Quantity must be integer")
        if qty <= 0:
            raise ValidationError("Quantity must be positive")
        return True

# =========================
# Models - الكلاسات الأساسية
# =========================
class User:
    """Model: User"""
    def __init__(self, username: str, password: str, usertype: str,
                 phonenumber: str, gender: str, isactive: bool = True):
        # لا تقم بالتحقق هنا من التكرار (يتم في UserManager)
        Validators.validate_username(username)
        Validators.validate_password(password)
        Validators.validate_usertype(usertype)
        Validators.validate_phonenumber(phonenumber)
        Validators.validate_gender(gender)

        self.username: str = username
        self.password: str = password  # ملاحظة: للتبسيط نخزن plain (يمكن تحسينه لاحقاً بالهاش)
        self.usertype: str = usertype.lower()
        self.phonenumber: str = phonenumber
        self.gender: str = gender
        self.isactive: bool = isactive

    def activate(self):
        self.isactive = True

    def deactivate(self):
        self.isactive = False

    def update(self, **kwargs):
        """تحديث الحقول المسموح بها"""
        if 'username' in kwargs:#kwarg = keyword argument
            Validators.validate_username(kwargs['username'])
            self.username = kwargs['username']
        if 'password' in kwargs and kwargs['password'] is not None:
            Validators.validate_password(kwargs['password'])
            self.password = kwargs['password']
        if 'phonenumber' in kwargs and kwargs['phonenumber'] is not None:
            Validators.validate_phonenumber(kwargs['phonenumber'])
            self.phonenumber = kwargs['phonenumber']
        if 'gender' in kwargs and kwargs['gender'] is not None:
            Validators.validate_gender(kwargs['gender'])
            self.gender = kwargs['gender']
        if 'isactive' in kwargs and kwargs['isactive'] is not None:
            self.isactive = bool(kwargs['isactive'])
        if 'usertype' in kwargs and kwargs['usertype'] is not None:
            Validators.validate_usertype(kwargs['usertype'])
            self.usertype = kwargs['usertype'].lower()

    def to_dict(self):
        """تحويل الكائن إلى قاموس لحفظه في JSON"""
        return {
            'username': self.username,
            'password': self.password,
            'usertype': self.usertype,
            'phonenumber': self.phonenumber,
            'gender': self.gender,
            'isactive': self.isactive
        }

    @classmethod
    def from_dict(cls, data):
        """إنشاء كائن من قاموس"""
        return cls(
            username=data['username'],
            password=data['password'],
            usertype=data['usertype'],
            phonenumber=data['phonenumber'],
            gender=data['gender'],
            isactive=data['isactive']
        )

    def __str__(self):
        return f"{self.username} ({self.usertype}) Active: {self.isactive}"

class Product:
    """Model: Product"""
    def __init__(self, pid: int, name: str, price: float, is_active: bool = True):
        Validators.validate_product_id(pid)
        Validators.validate_product_name(name)
        Validators.validate_price(price)

        self.id: int = pid
        self.name: str = name
        self.price: float = float(price)
        self.is_active: bool = is_active

    def update(self, **kwargs):
        if 'name' in kwargs and kwargs['name'] is not None:
            Validators.validate_product_name(kwargs['name'])
            self.name = kwargs['name']
        if 'price' in kwargs and kwargs['price'] is not None:
            Validators.validate_price(kwargs['price'])
            self.price = float(kwargs['price'])
        if 'is_active' in kwargs and kwargs['is_active'] is not None:
            self.is_active = bool(kwargs['is_active'])

    def to_dict(self):
        """تحويل الكائن إلى قاموس لحفظه في JSON"""
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'is_active': self.is_active
        }

    @classmethod
    def from_dict(cls, data):
        """إنشاء كائن من قاموس"""
        return cls(
            pid=data['id'],
            name=data['name'],
            price=data['price'],
            is_active=data['is_active']
        )

    def __str__(self):
        return f"{self.id} - {self.name} : {self.price} ({'active' if self.is_active else 'archived'})"

class OrderItem:
    """Model: OrderItem snapshot"""
    def __init__(self, product_id: int, quantity: int, price_at_order: float):
        Validators.validate_quantity(quantity)
        Validators.validate_price(price_at_order)
        self.product_id: int = product_id
        self.quantity: int = quantity
        self.price_at_order: float = float(price_at_order)

    def to_dict(self):
        """تحويل الكائن إلى قاموس لحفظه في JSON"""
        return {
            'product_id': self.product_id,
            'quantity': self.quantity,
            'price_at_order': self.price_at_order
        }

    @classmethod
    def from_dict(cls, data):
        """إنشاء كائن من قاموس"""
        return cls(
            product_id=data['product_id'],
            quantity=data['quantity'],
            price_at_order=data['price_at_order']
        )

    def __str__(self):
        return f"Product {self.product_id} x {self.quantity} @ {self.price_at_order}"

class Order:
    """Model: Order"""
    VALID_STATUSES = ("pending", "confirmed", "shipped", "delivered", "cancelled")

    def __init__(self, order_id: int, user_username: str):
        self.order_id: int = order_id
        self.user_username: str = user_username
        self.items: List[OrderItem] = []
        self.status: str = "pending"

    def add_item(self, item: OrderItem):
        self.items.append(item)

    def calculate_total(self) -> float:
        total = 0.0
        for it in self.items:
            total += it.quantity * it.price_at_order
        return total

    def update_status(self, new_status: str):
        if new_status not in Order.VALID_STATUSES:
            raise ValidationError(f"Invalid status. Must be one of: {Order.VALID_STATUSES}")
        self.status = new_status

    def to_dict(self):
        """تحويل الكائن إلى قاموس لحفظه في JSON"""
        return {
            'order_id': self.order_id,
            'user_username': self.user_username,
            'items': [item.to_dict() for item in self.items],
            'status': self.status
        }

    @classmethod
    def from_dict(cls, data):
        """إنشاء كائن من قاموس"""
        order = cls(
            order_id=data['order_id'],
            user_username=data['user_username']
        )
        order.status = data['status']
        for item_data in data['items']:
            order.add_item(OrderItem.from_dict(item_data))
        return order

    def __str__(self):
        return f"Order {self.order_id} by {self.user_username} status={self.status} items={len(self.items)} total={self.calculate_total()}"

# =========================
# Managers - إدارة البيانات
# =========================
class UserManager:
    """Manager: Users stored in-memory dictionary keyed by username"""
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.file_path = "users.txt"
        self.load_users()

    def load_users(self):
        """تحميل المستخدمين من الملف"""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    for user_data in data:
                        user = User.from_dict(user_data)
                        self.users[user.username] = user
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading users: {e}")
                self.users = {}

    def save_users(self):
        """حفظ المستخدمين في الملف"""
        try:
            with open(self.file_path, 'w', encoding='utf-8') as file:
                data = [user.to_dict() for user in self.users.values()]
                json.dump(data, file, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"Error saving users: {e}")

    def add_user(self, username: str, password: str, usertype: str,
                 phonenumber: str, gender: str, isactive: bool = True) -> User:
        # تحقق قبل الإنشاء: عدم التكرار + متطلبات الحقول
        Validators.validate_username(username, existing_usernames=list(self.users.keys()))
        Validators.validate_password(password)
        Validators.validate_usertype(usertype)
        Validators.validate_phonenumber(phonenumber)
        Validators.validate_gender(gender)

        user = User(username=username, password=password, usertype=usertype,
                    phonenumber=phonenumber, gender=gender, isactive=isactive)
        self.users[username] = user
        self.save_users()  # حفظ التغييرات في الملف
        return user

    def update_user(self, username: str, **kwargs) -> User:
        if username not in self.users:
            raise NotFoundError("User not found")
        user = self.users[username]
        # إذا تم تغيير الاسم يجب التأكد من عدم تكراره
        if 'username' in kwargs and kwargs['username'] != username:
            Validators.validate_username(kwargs['username'], existing_usernames=list(self.users.keys()))
            # نقل المفتاح في القاموس
            new_username = kwargs['username']
            del self.users[username]
            user.username = new_username
            self.users[new_username] = user
            # استبدال username المرجعي
            username = new_username
        # تحديث بقية الحقول
        user.update(**kwargs)
        self.save_users()  # حفظ التغييرات في الملف
        return user

    def delete_user(self, username: str) -> bool:
        if username not in self.users:
            raise NotFoundError("User not found")
        del self.users[username]
        self.save_users()  # حفظ التغييرات في الملف
        return True

    def find_user(self, username: str) -> Optional[User]:
        return self.users.get(username)

    def list_users(self) -> List[User]:
        return list(self.users.values())

    def activate_user(self, username: str) -> bool:
        user = self.find_user(username)
        if not user:
            raise NotFoundError("User not found")
        user.activate()
        self.save_users()  # حفظ التغييرات في الملف
        return True

    def deactivate_user(self, username: str) -> bool:
        user = self.find_user(username)
        if not user:
            raise NotFoundError("User not found")
        user.deactivate()
        self.save_users()  # حفظ التغييرات في الملف
        return True

class ProductManager:
    """Manager: Products stored keyed by integer id"""
    def __init__(self):
        self.products: Dict[int, Product] = {}
        self.next_id: int = 1
        self.file_path = "products.txt"
        self.load_products()

    def load_products(self):
        """تحميل المنتجات من الملف"""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    for product_data in data:
                        product = Product.from_dict(product_data)
                        self.products[product.id] = product
                        if product.id >= self.next_id:
                            self.next_id = product.id + 1
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading products: {e}")
                self.products = {}
                self.next_id = 1

    def save_products(self):
        """حفظ المنتجات في الملف"""
        try:
            with open(self.file_path, 'w', encoding='utf-8') as file:
                data = [product.to_dict() for product in self.products.values()]
                json.dump(data, file, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"Error saving products: {e}")

    def add_product(self, name: str, price: float) -> Product:
        Validators.validate_product_name(name)
        Validators.validate_price(price)
        pid = self.next_id
        product = Product(pid, name, float(price), is_active=True)
        self.products[pid] = product
        self.next_id += 1
        self.save_products()  # حفظ التغييرات في الملف
        return product

    def update_product(self, pid: int, **kwargs) -> Product:
        if pid not in self.products:
            raise NotFoundError("Product not found")
        prod = self.products[pid]
        prod.update(**kwargs)
        self.save_products()  # حفظ التغييرات في الملف
        return prod

    def delete_product(self, pid: int, allow_archive: bool = True) -> bool:
        """لا نحذف المنتج نهائياً - نختار أرشفته (is_active=False) لسلامة الفواتير"""
        if pid not in self.products:
            raise NotFoundError("Product not found")
        if allow_archive:
            self.products[pid].is_active = False
            self.save_products()  # حفظ التغييرات في الملف
            return True
        else:
            del self.products[pid]
            self.save_products()  # حفظ التغييرات في الملف
            return True

    def find_product(self, pid: int) -> Optional[Product]:
        return self.products.get(pid)

    def list_products(self, include_inactive: bool = False) -> List[Product]:
        if include_inactive:
            return list(self.products.values())
        return [p for p in self.products.values() if p.is_active]

class OrderManager:
    """Manager: Orders stored keyed by integer order_id"""
    def __init__(self, product_manager: ProductManager):
        self.orders: Dict[int, Order] = {}
        self.next_order_id: int = 1
        self.product_manager = product_manager
        self.file_path = "orders.txt"
        self.load_orders()

    def load_orders(self):
        """تحميل الطلبات من الملف"""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    for order_data in data:
                        order = Order.from_dict(order_data)
                        self.orders[order.order_id] = order
                        if order.order_id >= self.next_order_id:
                            self.next_order_id = order.order_id + 1
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading orders: {e}")
                self.orders = {}
                self.next_order_id = 1

    def save_orders(self):
        """حفظ الطلبات في الملف"""
        try:
            with open(self.file_path, 'w', encoding='utf-8') as file:
                data = [order.to_dict() for order in self.orders.values()]
                json.dump(data, file, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"Error saving orders: {e}")

    def create_order(self, customer_username: str, items: List[Tuple[int, int]]) -> Order:
        """items: list of tuples (product_id, quantity)"""
        # تحقق وجود العميل يتحقق في مكان آخر (System)
        oid = self.next_order_id
        order = Order(oid, customer_username)
        # تحقق من وجود المنتجات وكميات صحيحة ثم أضف snapshot بأسعار وقت الطلب
        for pid, qty in items:
            product = self.product_manager.find_product(pid)
            if not product:
                raise NotFoundError(f"Product {pid} not found")
            if not product.is_active:
                raise ValidationError(f"Product {pid} is not active")
            Validators.validate_quantity(qty)
            order_item = OrderItem(product_id=pid, quantity=qty, price_at_order=product.price)
            order.add_item(order_item)
        self.orders[oid] = order
        self.next_order_id += 1
        self.save_orders()  # حفظ التغييرات في الملف
        return order

    def find_order(self, order_id: int) -> Optional[Order]:
        return self.orders.get(order_id)

    def list_orders(self) -> List[Order]:
        return list(self.orders.values())

    def list_user_orders(self, username: str) -> List[Order]:
        return [o for o in self.orders.values() if o.user_username == username]

    def update_order_status(self, order_id: int, new_status: str) -> Order:
        order = self.find_order(order_id)
        if not order:
            raise NotFoundError("Order not found")
        order.update_status(new_status.lower())
        self.save_orders()  # حفظ التغييرات في الملف
        return order

# =========================
# System: واجهة التطبيق و Console Menu
# =========================
class System:
    def __init__(self):
        self.user_manager = UserManager()
        self.product_manager = ProductManager()
        self.order_manager = OrderManager(self.product_manager)
        self.current_user: Optional[User] = None

        # إنشاء مستخدم Admin افتراضي (يمكن تغييره أو حذفه)
        try:
            # إذا حاولت الإضافة مرتين ستُرفع استثناء ValidationError عن التكرار، لذا إحطه في try
            self.user_manager.add_user("admin", "Adm!n1234", "admin", "771234567", "male")
        except ValidationError:
            pass

    # -------------------------
    # Authentication methods
    # -------------------------
    def login(self, username: str, password: str) -> User:
        user = self.user_manager.find_user(username)
        if not user:
            raise AuthenticationError("Username not found")
        if not user.isactive:
            raise AuthenticationError("User account is not active")
        if user.password != password:
            raise AuthenticationError("Incorrect password")
        self.current_user = user
        return user

    def logout(self):
        self.current_user = None

    def is_logged_in(self) -> bool:
        return self.current_user is not None

    def require_role(self, roles: List[str]):
        if not self.is_logged_in():
            raise AuthorizationError("You must be logged in")
        if self.current_user.usertype not in [r.lower() for r in roles]:
            raise AuthorizationError("You don't have the required role")

    # -------------------------
    # CLI helpers (Input safe)
    # -------------------------
    def safe_input(self, prompt: str) -> str:
        try:
            return input(prompt)
        except (KeyboardInterrupt, EOFError):
            print("\nInput cancelled. Exiting.")
            sys.exit(0)

    def safe_int(self, prompt: str, allow_empty: bool = False) -> Optional[int]:
        while True:
            val = self.safe_input(prompt)
            if allow_empty and val.strip() == "":
                return None
            try:
                return int(val)
            except ValueError:
                print("Please enter a valid integer.")

    def safe_float(self, prompt: str, allow_empty: bool = False) -> Optional[float]:
        while True:
            val = self.safe_input(prompt)
            if allow_empty and val.strip() == "":
                return None
            try:
                return float(val)
            except ValueError:
                print("Please enter a valid number.")

    # -------------------------
    # Menus and actions
    # -------------------------
    def run(self):
        """الدخول الرئيسي - loop"""
        print("Welcome to Users-Products-Orders System")
        while True:
            try:
                if not self.is_logged_in():
                    print("\n1) Login\n2) Exit")
                    choice = self.safe_input("Choose: ").strip()
                    if choice == "1":
                        self.cli_login()
                    elif choice == "2":
                        print("Goodbye.")
                        break
                    else:
                        print("Invalid choice.")
                else:
                    # بعد تسجيل الدخول نعرض قوائم مختلفة حسب الدور
                    ut = self.current_user.usertype
                    print(f"\nLogged in as {self.current_user.username} ({ut})")
                    if ut == "admin":
                        self.menu_admin()
                    elif ut == "employee":
                        self.menu_employee()
                    elif ut == "customer":
                        self.menu_customer()
                    else:
                        print("Unknown user type. Logging out.")
                        self.logout()
            except (ValidationError, AuthenticationError, AuthorizationError, NotFoundError) as e:
                print("Error:", e)
            except Exception as e:
                print("Unexpected error:", e)

    # -------------------------
    # Login CLI
    # -------------------------
    def cli_login(self):
        username = self.safe_input("Username: ").strip()
        password = self.safe_input("Password: ").strip()
        try:
            self.login(username, password)
            print(f"Login successful. Welcome {self.current_user.username}")
        except AuthenticationError as e:
            print("Login failed:", e)

    # -------------------------
    # Admin menu
    # -------------------------
    def menu_admin(self):
        while True:
            print("\n--- Admin Menu ---")
            print("1) User Management")
            print("2) Product Management")
            print("3) Order Management")
            print("4) Reports")
            print("5) Logout")
            choice = self.safe_input("Choose: ").strip()
            if choice == "1":
                self.menu_user_management()
            elif choice == "2":
                self.menu_product_management()
            elif choice == "3":
                self.menu_order_management()
            elif choice == "4":
                self.menu_reports()
            elif choice == "5":
                self.logout()
                break
            else:
                print("Invalid choice.")

    # -------------------------
    # Employee menu
    # -------------------------
    def menu_employee(self):
        while True:
            print("\n--- Employee Menu ---")
            print("1) Product Management")
            print("2) Order Management")
            print("3) Logout")
            choice = self.safe_input("Choose: ").strip()
            if choice == "1":
                self.menu_product_management()
            elif choice == "2":
                self.menu_order_management()
            elif choice == "3":
                self.logout()
                break
            else:
                print("Invalid choice.")

    # -------------------------
    # Customer menu
    # -------------------------
    def menu_customer(self):
        while True:
            print("\n--- Customer Menu ---")
            print("1) View Products")
            print("2) Create Order")
            print("3) My Orders")
            print("4) Logout")
            choice = self.safe_input("Choose: ").strip()
            if choice == "1":
                self.action_list_products()
            elif choice == "2":
                self.action_create_order()
            elif choice == "3":
                self.action_my_orders()
            elif choice == "4":
                self.logout()
                break
            else:
                print("Invalid choice.")

    # -------------------------
    # User Management (Admin)
    # -------------------------
    def menu_user_management(self):
        self.require_role(['admin'])
        while True:
            print("\n--- User Management ---")
            print("1) Add User")
            print("2) Update User")
            print("3) Delete User")
            print("4) List Users")
            print("5) Activate User")
            print("6) Deactivate User")
            print("7) Back")
            choice = self.safe_input("Choose: ").strip()
            if choice == "1":
                self.action_add_user()
            elif choice == "2":
                self.action_update_user()
            elif choice == "3":
                self.action_delete_user()
            elif choice == "4":
                self.action_list_users()
            elif choice == "5":
                self.action_activate_user()
            elif choice == "6":
                self.action_deactivate_user()
            elif choice == "7":
                break
            else:
                print("Invalid choice.")

    def action_add_user(self):
        print("\n--- Add User ---")
        username = self.safe_input("Username: ").strip()
        password = self.safe_input("Password: ").strip()
        usertype = self.safe_input("User type (admin/employee/customer): ").strip().lower()
        phonenumber = self.safe_input("Phone number: ").strip()
        gender = self.safe_input("Gender (m/f): ").strip()
        try:
            user = self.user_manager.add_user(username, password, usertype, phonenumber, gender)
            print(f"User '{user.username}' added successfully.")
        except ValidationError as e:
            print("Failed to add user:", e)

    def action_update_user(self):
        print("\n--- Update User ---")
        username = self.safe_input("Username to update: ").strip()
        user = self.user_manager.find_user(username)
        if not user:
            print("User not found")
            return
        print("Leave blank to keep current value.")
        new_username = self.safe_input(f"New username [{user.username}]: ").strip() or user.username
        new_password = self.safe_input("New password (leave blank to keep): ").strip() or None
        new_usertype = self.safe_input(f"New usertype [{user.usertype}]: ").strip() or user.usertype
        new_phone = self.safe_input(f"New phone [{user.phonenumber}]: ").strip() or user.phonenumber
        new_gender = self.safe_input(f"New gender [{user.gender}]: ").strip() or user.gender
        try:
            updated = self.user_manager.update_user(username,
                                                   username=new_username,
                                                   password=new_password,
                                                   usertype=new_usertype,
                                                   phonenumber=new_phone,
                                                   gender=new_gender)
            print("User updated.")
        except (ValidationError, NotFoundError) as e:
            print("Failed to update user:", e)

    def action_delete_user(self):
        print("\n--- Delete User ---")
        username = self.safe_input("Username to delete: ").strip()
        try:
            self.user_manager.delete_user(username)
            print("User deleted.")
        except NotFoundError as e:
            print("Error:", e)

    def action_list_users(self):
        print("\n--- All Users ---")
        users = self.user_manager.list_users()
        if not users:
            print("No users found.")
            return
        for u in users:
            print(f"- {u}")

    def action_activate_user(self):
        username = self.safe_input("Username to activate: ").strip()
        try:
            self.user_manager.activate_user(username)
            print("User activated.")
        except NotFoundError as e:
            print("Error:", e)

    def action_deactivate_user(self):
        username = self.safe_input("Username to deactivate: ").strip()
        try:
            self.user_manager.deactivate_user(username)
            print("User deactivated.")
        except NotFoundError as e:
            print("Error:", e)

    # -------------------------
    # Product Management
    # -------------------------
    def menu_product_management(self):
        # allow admin and employee
        if self.current_user.usertype not in ('admin', 'employee'):
            raise AuthorizationError("You don't have permission to manage products")
        while True:
            print("\n--- Product Management ---")
            print("1) Add Product")
            print("2) Update Product")
            print("3) Delete(Archive) Product")
            print("4) List Products")
            print("5) Back")
            choice = self.safe_input("Choose: ").strip()
            if choice == "1":
                self.action_add_product()
            elif choice == "2":
                self.action_update_product()
            elif choice == "3":
                self.action_delete_product()
            elif choice == "4":
                self.action_list_products()
            elif choice == "5":
                break
            else:
                print("Invalid choice.")

    def action_add_product(self):
        print("\n--- Add Product ---")
        name = self.safe_input("Product name: ").strip()
        price = self.safe_float("Product price: ")
        try:
            product = self.product_manager.add_product(name, price)
            print(f"Product added: {product}")
        except ValidationError as e:
            print("Failed to add product:", e)

    def action_update_product(self):
        print("\n--- Update Product ---")
        pid = self.safe_int("Product ID to update: ")
        prod = self.product_manager.find_product(pid)
        if not prod:
            print("Product not found.")
            return
        print("Leave blank to keep current value.")
        new_name = self.safe_input(f"New name [{prod.name}]: ").strip() or prod.name
        new_price_input = self.safe_input(f"New price [{prod.price}]: ").strip()
        new_price = float(new_price_input) if new_price_input else prod.price
        try:
            updated = self.product_manager.update_product(pid, name=new_name, price=new_price)
            print("Product updated:", updated)
        except (ValidationError, NotFoundError) as e:
            print("Failed to update product:", e)

    def action_delete_product(self):
        print("\n--- Delete(Archive) Product ---")
        pid = self.safe_int("Product ID to delete/archive: ")
        try:
            self.product_manager.delete_product(pid, allow_archive=True)
            print("Product archived (is_active=False).")
        except NotFoundError as e:
            print("Error:", e)

    def action_list_products(self):
        print("\n--- Products ---")
        prods = self.product_manager.list_products(include_inactive=False)
        if not prods:
            print("No active products.")
            return
        for p in prods:
            print(f"- {p}")

    # -------------------------
    # Order Management
    # -------------------------
    def menu_order_management(self):
        # accessible by admin and employee
        if self.current_user.usertype not in ('admin', 'employee'):
            raise AuthorizationError("You don't have permission to manage orders")
        while True:
            print("\n--- Order Management ---")
            print("1) List Orders")
            print("2) Update Order Status")
            print("3) View Order Details")
            print("4) Back")
            choice = self.safe_input("Choose: ").strip()
            if choice == "1":
                self.action_list_orders()
            elif choice == "2":
                self.action_update_order_status()
            elif choice == "3":
                self.action_view_order_details()
            elif choice == "4":
                break
            else:
                print("Invalid choice.")

    def action_list_orders(self):
        orders = self.order_manager.list_orders()
        if not orders:
            print("No orders found.")
            return
        for o in orders:
            print(f"- {o}")

    def action_update_order_status(self):
        order_id = self.safe_int("Order ID: ")
        new_status = self.safe_input("New status (pending/confirmed/shipped/delivered/cancelled): ").strip().lower()
        try:
            order = self.order_manager.update_order_status(order_id, new_status)
            print("Order updated:", order)
        except (NotFoundError, ValidationError) as e:
            print("Error:", e)

    def action_view_order_details(self):
        order_id = self.safe_int("Order ID: ")
        order = self.order_manager.find_order(order_id)
        if not order:
            print("Order not found.")
            return
        print(order)
        for it in order.items:
            print("  -", it)
        print("Total:", order.calculate_total())

    # -------------------------
    # Customer actions
    # -------------------------
    def action_create_order(self):
        self.require_role(['customer'])
        print("\n--- Create Order ---")
        print("Enter product id and quantity. Type 'done' when finished.")
        items: List[Tuple[int, int]] = []
        while True:
            pid_raw = self.safe_input("Product ID (or 'done'): ").strip()
            if pid_raw.lower() == 'done':
                break
            try:
                pid = int(pid_raw)
            except ValueError:
                print("Enter a valid integer product id.")
                continue
            qty = self.safe_int("Quantity: ")
            items.append((pid, qty))
        try:
            order = self.order_manager.create_order(self.current_user.username, items)
            print(f"Order created with ID: {order.order_id}")
            print("Order total:", order.calculate_total())
        except (ValidationError, NotFoundError) as e:
            print("Failed to create order:", e)

    def action_my_orders(self):
        self.require_role(['customer'])
        orders = self.order_manager.list_user_orders(self.current_user.username)
        if not orders:
            print("You have no orders.")
            return
        for o in orders:
            print(f"- {o}")
            for it in o.items:
                print("   -", it)
            print("   Total:", o.calculate_total())

    # -------------------------
    # Reports (Admin)
    # -------------------------
    def menu_reports(self):
        self.require_role(['admin'])
        print("\n--- Reports ---")
        users = self.user_manager.list_users()
        products = self.product_manager.list_products(include_inactive=True)
        orders = self.order_manager.list_orders()
        print(f"Total users: {len(users)}")
        print(f"Total products (including archived): {len(products)}")
        print(f"Total orders: {len(orders)}")
        # simple stats
        by_type = {}
        for u in users:
            by_type[u.usertype] = by_type.get(u.usertype, 0) + 1
        print("Users by type:", by_type)
        totals = [o.calculate_total() for o in orders]
        print("Total revenue (sum of orders):", sum(totals))

# =========================
# Run system if main
# =========================
if __name__ == "__main__":
    app = System()
    app.run()

