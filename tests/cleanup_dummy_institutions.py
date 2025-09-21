#!/usr/bin/env python3
"""
Script to clean up dummy test institutions from Firebase.
This will remove test institutions and keep only real ones.
"""

import asyncio
from app.services.firestore import FirestoreService


async def cleanup_dummy_institutions():
    """Remove dummy/test institutions from Firebase."""
    print("🧹 Cleaning up dummy institutions from Firebase...")
    
    try:
        fs = FirestoreService()
        
        # Get all institutions
        print("\n📋 Current institutions in database:")
        institutions = await fs.list_institutions()
        
        for inst in institutions:
            name = inst.institution_name
            region = inst.region
            inst_id = inst.institution_id
            print(f"  - {name} ({region}) - ID: {inst_id}")
        
        # Define dummy/test institution names to remove
        dummy_names = [
            "Delhi University",
            "Mumbai University",
            "Bangalore Institute of Technology",
            "Anna University",
            "Jawaharlal Nehru University"
        ]
        
        print(f"\n🗑️  Removing {len(dummy_names)} test institutions...")
        
        removed_count = 0
        for inst in institutions:
            if inst.institution_name in dummy_names:
                print(f"  🗑️  Removing: {inst.institution_name}")
                # Delete the institution document
                await fs.db.collection("institutions").document(
                    inst.institution_id
                ).delete()
                removed_count += 1
            else:
                name = inst.institution_name
                print(f"  ✅ Keeping: {name} (real institution)")
        
        count = removed_count
        print(f"\n✨ Cleanup completed! Removed {count} dummy institutions.")
        
        # Show remaining institutions
        print("\n📋 Remaining institutions:")
        remaining_institutions = await fs.list_institutions()
        if remaining_institutions:
            for inst in remaining_institutions:
                print(f"  - {inst.institution_name} ({inst.region})")
        else:
            print("  No institutions remaining (database is clean)")
            
        print(f"\nTotal remaining institutions: {len(remaining_institutions)}")
        
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(cleanup_dummy_institutions())
