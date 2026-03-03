from app.database import SessionLocal
from app.models import User, Book

db = SessionLocal()

print("="*60)
print("DATABASE CHECK FOR LOAD TESTING")
print("="*60)

# Check user
print("\n1. Checking User...")
user = db.query(User).filter(User.username == "admin").first()
if user:
    print(f"   ✅ User 'user123123' EXISTS")
    print(f"   Role: {user.role}")
else:
    print("   ❌ User 'user123123' NOT FOUND!")
    print("   You need to create this user first!")

# Check books
print("\n2. Checking Books...")
all_books = db.query(Book).all()
print(f"   Total books in database: {len(all_books)}")

if len(all_books) > 0:
    min_id = min(b.id for b in all_books)
    max_id = max(b.id for b in all_books)
    print(f"   Book ID range: {min_id} to {max_id}")
    
    # Check specific range 210-244
    target_books = db.query(Book).filter(Book.id >= 210, Book.id <= 244).all()
    print(f"\n   Books in range 210-244: {len(target_books)} books")
    
    if len(target_books) == 0:
        print("   ❌ WARNING: No books in range 210-244!")
        print(f"   Your Locust file tries to access books 210-244")
        print(f"   But your database has books {min_id}-{max_id}")
        print(f"\n   SOLUTION: Update locustfile_comprehensive.py:")
        print(f"   Change: random.randint(210, 244)")
        print(f"   To:     random.randint({min_id}, {max_id})")
    else:
        print(f"   ✅ Books available: {[b.id for b in target_books[:5]]}{'...' if len(target_books) > 5 else ''}")
        
        # Check availability
        available = sum(1 for b in target_books if b.available_copies > 0)
        print(f"   Available for borrowing: {available}/{len(target_books)}")
else:
    print("   ❌ NO BOOKS IN DATABASE!")
    print("   You need to add books first!")

print("\n" + "="*60)
print("RECOMMENDATION:")
print("="*60)

if not user:
    print("⚠️  Create user first: POST /api/register")
    print('   {"username": "user123123", "password": "admin", "email": "user@test.com", "full_name": "Test User"}')

if len(all_books) == 0:
    print("⚠️  Add books to database first!")
elif len(target_books) == 0:
    print(f"⚠️  Update book ID ranges in locustfile to: random.randint({min_id}, {max_id})")
else:
    print("✅ Ready for load testing!")

db.close()