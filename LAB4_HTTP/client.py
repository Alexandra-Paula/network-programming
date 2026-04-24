import requests
import json

BASE_URL = "http://localhost:5000/api/category"

def print_menu():
    print("\nUTM Shop")
    print("1. List categories")
    print("2. Category details")
    print("3. Create new category")
    print("4. Delete category")
    print("5. Update category title")
    print("6. Create product in category")
    print("7. List products in category")
    print("0. Exit")

def read_int(prompt):
    while True:
        try:
            return int(input(prompt).strip())
        except ValueError:
            print("Enter a valid integer!")

def read_float(prompt):
    while True:
        try:
            return float(input(prompt).strip().replace(",", "."))
        except ValueError:
            print("Enter a valid decimal number (ex: 2.99).")

def print_error(code, message):
    print(f"[HTTP {code}] {message}")

def print_success(message):
    print(f"{message}")

# 1 list categories
# GET /api/category/categories
def list_categories():
    print("\nList Categories")
    response = requests.get(f"{BASE_URL}/categories")

    if response.status_code == 404:
        print_error(404, "No categories found.")
        return
    if not response.ok:
        print_error(response.status_code, "Error fetching categories.")
        return

    categories = response.json()
    if not categories:
        print("(List is empty)")
        return

    print(f"\n{'ID':<6} {'Name':<30} {'Products':>8}")
    print("-" * 46)
    for cat in categories:
        print(f"{cat['id']:<6} {cat.get('name') or '(no title)':<30} {cat.get('itemsCount', 0):>8}")
    print("-" * 46)
    print(f"Total: {len(categories)} category(ies)")

# 2 category details
# GET /api/category/categories/{id}
def get_category():
    print("\nCategory Details")
    cat_id = read_int("Category ID: ")

    response = requests.get(f"{BASE_URL}/categories/{cat_id}")

    if response.status_code == 404:
        print_error(404, f"Category with ID={cat_id} not found.")
        return
    if not response.ok:
        print_error(response.status_code, "Error.")
        return

    categories = response.json()
    if not categories:
        print("No results.")
        return

    print(f"\n{'ID':<6} {'Name':<30} {'Products':>8}")
    print("-" * 46)
    for cat in categories:
        print(f"{cat['id']:<6} {cat.get('name') or '(no title)':<30} {cat.get('itemsCount', 0):>8}")

# 3 create category
# POST /api/category/categories   Body: { "title": "..." }
def create_category():
    print("\nCreate New Category")
    title = input("Category title: ").strip()

    if not title:
        print("Title cannot be empty.")
        return

    payload = {"title": title}
    response = requests.post(f"{BASE_URL}/categories", json=payload)

    if response.status_code == 409:
        print_error(409, f'A category with title "{title}" already exists!')
        return
    if not response.ok:
        print_error(response.status_code, "Creation failed.")
        return

    created = response.json()
    print_success(f"Category created! ID={created['id']}, Title=\"{created.get('name')}\"")

# 4 delete category
# DELETE /api/category/categories/{id}
def delete_category():
    print("\nDelete Category")
    cat_id = read_int("Category ID to delete: ")

    confirm = input(f"Are you sure you want to delete category ID={cat_id}? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("Operation cancelled.")
        return

    response = requests.delete(f"{BASE_URL}/categories/{cat_id}")

    if response.status_code == 404:
        print_error(404, f"Category with ID={cat_id} not found.")
        return
    if not response.ok:
        print_error(response.status_code, "Deletion failed.")
        return

    print_success(f"Category ID={cat_id} has been deleted.")

# 5 update category title
# PUT /api/category/{id}   Body: { "title": "..." }
def update_category():
    print("\nUpdate Category Title")
    cat_id = read_int("Category ID: ")
    new_title = input("New title: ").strip()

    if not new_title:
        print("Title cannot be empty.")
        return

    payload = {"title": new_title}
    response = requests.put(f"{BASE_URL}/{cat_id}", json=payload)

    if response.status_code == 409:
        print_error(409, f'A category with title "{new_title}" already exists.')
        return
    if response.status_code == 404:
        print_error(404, f"Category with ID={cat_id} not found.")
        return
    if not response.ok:
        print_error(response.status_code, "Update failed.")
        return

    updated = response.json()
    print_success(f"Category ID={cat_id} title updated to \"{updated.get('name')}\".")

# 6 create product in category
# POST /api/category/categories/{id}/products   Body: ProductShortDto
def create_product():
    print("\nCreate New Product")
    cat_id = read_int("Category ID: ")
    title = input("Product title: ").strip()

    if not title:
        print("Title cannot be empty.")
        return

    price = read_float("Price (ex: 29.99): ")

    payload = {
        "id": 0,
        "title": title,
        "price": price,
        "categoryId": cat_id
    }
    response = requests.post(f"{BASE_URL}/categories/{cat_id}/products", json=payload)

    if response.status_code == 404:
        print_error(404, f"Category with ID={cat_id} not found.")
        return
    if not response.ok:
        print_error(response.status_code, "Product creation failed.")
        return

    created = response.json()
    print_success(f"Product created! ID={created['id']}, Title=\"{created['title']}\", Price={created['price']:.2f}")

# 7 list products in category
# GET /api/category/categories/{id}/products
def list_products():
    print("\nProducts in Category")
    cat_id = read_int("Category ID: ")

    response = requests.get(f"{BASE_URL}/categories/{cat_id}/products")

    if response.status_code == 404:
        print_error(404, f"Category with ID={cat_id} not found or has no products.")
        return
    if not response.ok:
        print_error(response.status_code, "Error.")
        return

    products = response.json()
    if not products:
        print("(Category has no products)")
        return

    print(f"\n{'ID':<6} {'Title':<30} {'Price':>10}")
    print("-" * 48)
    for p in products:
        print(f"{p['id']:<6} {p.get('title') or '(no title)':<30} {p['price']:>10.2f}")
    print("-" * 48)
    print(f"Total: {len(products)} product(s)")

def main():
    actions = {
        "1": list_categories,
        "2": get_category,
        "3": create_category,
        "4": delete_category,
        "5": update_category,
        "6": create_product,
        "7": list_products,
    }

    while True:
        print_menu()
        choice = input("Choice: ").strip()

        if choice == "0":
            print("Goodbye!")
            break
        elif choice in actions:
            try:
                actions[choice]()
            except requests.exceptions.ConnectionError:
                print("\n[Connection error] Cannot reach the server.")
                print(f"Make sure UtmShop is running at: {BASE_URL}")
            except Exception as e:
                print(f"\n[Unexpected error] {e}")
        else:
            print("Invalid option.")

        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
