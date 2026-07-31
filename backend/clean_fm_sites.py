from app.core.database import SessionLocal
from app.models.fleet_manager import FleetManager

def cleanup_fleet_managers():
    db = SessionLocal()
    try:
        # Find any user ID with multiple FleetManager entries
        fms = db.query(FleetManager).all()
        user_sites = {}
        duplicates_to_delete = []
        
        for fm in fms:
            if fm.user_id in user_sites:
                print(f"User {fm.user_id} is already assigned to site {user_sites[fm.user_id]}. Marking FM {fm.id} (site {fm.site_id}) for deletion.")
                duplicates_to_delete.append(fm)
            else:
                user_sites[fm.user_id] = fm.site_id
                
        for dup in duplicates_to_delete:
            db.delete(dup)
            
        if duplicates_to_delete:
            db.commit()
            print(f"Deleted {len(duplicates_to_delete)} duplicate fleet manager assignments.")
        else:
            print("No duplicate fleet manager assignments found. 1-to-1 mapping is valid.")
            
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    cleanup_fleet_managers()
