import Foundation
import CoreData

class CoreDataManager {
    static let shared = CoreDataManager()
    
    private init() {}
    
    lazy var persistentContainer: NSPersistentContainer = {
        let container = NSPersistentContainer(name: "WeightLossBetting")
        container.loadPersistentStores { description, error in
            if let error = error {
                fatalError("Unable to load persistent stores: \(error)")
            }
        }
        return container
    }()
    
    var context: NSManagedObjectContext {
        return persistentContainer.viewContext
    }
    
    func saveContext() {
        let context = persistentContainer.viewContext
        if context.hasChanges {
            do {
                try context.save()
            } catch {
                let nserror = error as NSError
                fatalError("Unresolved error \(nserror), \(nserror.userInfo)")
            }
        }
    }
    
    // MARK: - User Cache
    
    func cacheUser(_ user: User) {
        // Disabled to avoid CoreData model loading errors
        print("⚠️ CoreData caching disabled for user: \(user.nickname)")
    }
    
    func getCachedUser(id: String) -> User? {
        let fetchRequest: NSFetchRequest<UserEntity> = UserEntity.fetchRequest()
        fetchRequest.predicate = NSPredicate(format: "id == %@", id)
        
        do {
            let results = try context.fetch(fetchRequest)
            return results.first?.toUser()
        } catch {
            print("Error fetching cached user: \(error)")
            return nil
        }
    }
    
    // MARK: - Betting Plan Cache
    
    func cacheBettingPlan(_ plan: BettingPlan) {
        // Disabled to avoid CoreData model loading errors
        print("⚠️ CoreData caching disabled for plan: \(plan.id)")
    }
    
    func getCachedBettingPlans(userId: String) -> [BettingPlan] {
        let fetchRequest: NSFetchRequest<BettingPlanEntity> = BettingPlanEntity.fetchRequest()
        fetchRequest.predicate = NSPredicate(format: "creatorId == %@ OR participantId == %@", userId, userId)
        
        do {
            let results = try context.fetch(fetchRequest)
            return results.compactMap { $0.toBettingPlan() }
        } catch {
            print("Error fetching cached plans: \(error)")
            return []
        }
    }
    
    // MARK: - Offline Check-In Queue
    
    func cacheCheckIn(_ checkIn: CheckIn) {
        // Disabled to avoid CoreData model loading errors
        print("⚠️️ CoreData caching disabled for check-in: \(checkIn.id)")
    }
    
    func getCachedCheckIns(planId: String) -> [CheckIn] {
        // Disabled to avoid CoreData model loading errors
        print("⚠️️ CoreData caching disabled for getting check-ins: \(planId)")
        return []
    }

    // MARK: - Offline Check-In Queue
    
    func saveOfflineCheckIn(planId: String, weight: Double, note: String?, photoUrl: String?, userId: String) {
        let entity = OfflineCheckInEntity(context: context)
        entity.id = UUID().uuidString
        entity.userId = userId
        entity.planId = planId
        entity.weight = weight
        entity.note = note
        entity.photoUrl = photoUrl
        entity.createdAt = Date()
        entity.synced = false
        
        saveContext()
    }
    
    func getOfflineCheckIns() -> [OfflineCheckInEntity] {
        let fetchRequest: NSFetchRequest<OfflineCheckInEntity> = OfflineCheckInEntity.fetchRequest()
        fetchRequest.predicate = NSPredicate(format: "synced == NO")
        
        do {
            return try context.fetch(fetchRequest)
        } catch {
            print("Error fetching offline check-ins: \(error)")
            return []
        }
    }
    
    func markCheckInAsSynced(id: String) {
        let fetchRequest: NSFetchRequest<OfflineCheckInEntity> = OfflineCheckInEntity.fetchRequest()
        fetchRequest.predicate = NSPredicate(format: "id == %@", id)
        
        do {
            let results = try context.fetch(fetchRequest)
            if let entity = results.first {
                entity.synced = true
                saveContext()
            }
        } catch {
            print("Error marking check-in as synced: \(error)")
        }
    }
    
    // MARK: - Clear Cache
    
    func clearAllCache() {
        let entities = ["UserEntity", "BettingPlanEntity", "CheckInEntity", "OfflineCheckInEntity"]
        
        for entityName in entities {
            let fetchRequest = NSFetchRequest<NSFetchRequestResult>(entityName: entityName)
            let deleteRequest = NSBatchDeleteRequest(fetchRequest: fetchRequest)
            
            do {
                try context.execute(deleteRequest)
                saveContext()
            } catch {
                print("Error clearing \(entityName): \(error)")
            }
        }
    }
}

// MARK: - Entity Extensions

extension UserEntity {
    func toUser() -> User? {
        guard let gender = Gender(rawValue: gender) else {
            return nil
        }
        
        return User(
            id: id,
            email: email,
            nickname: nickname,
            gender: gender,
            age: Int(age),
            height: height,
            currentWeight: currentWeight,
            targetWeight: targetWeight > 0 ? targetWeight : nil,
            paymentMethod: nil,
            createdAt: Date(),
            updatedAt: updatedAt ?? Date()
        )
    }
}

extension BettingPlanEntity {
    func toBettingPlan() -> BettingPlan? {
        guard let status = PlanStatus(rawValue: status) else {
            return nil
        }
        
        // Note: CoreData model doesn't have all fields, return minimal plan
        // This is mainly used for offline cache, so using default values is acceptable
        return BettingPlan(
            id: id,
            creatorId: creatorId,
            creatorNickname: nil,
            creatorEmail: nil,
            participantId: participantId,
            participantNickname: nil,
            participantEmail: nil,
            status: status,
            betAmount: betAmount,
            startDate: startDate,
            endDate: endDate,
            description: planDescription,
            creatorInitialWeight: 0,
            creatorTargetWeight: 0,
            creatorTargetWeightLoss: 0,
            participantInitialWeight: nil,
            participantTargetWeight: nil,
            participantTargetWeightLoss: nil,
            createdAt: updatedAt ?? Date(),
            activatedAt: nil,
            abandonedBy: nil,
            abandonedAt: nil,
            expiryCheckedAt: nil
        )
    }
}

extension CheckInEntity {
    func toCheckIn() -> CheckIn? {
        guard let reviewStatus = ReviewStatus(rawValue: reviewStatus) else {
            return nil
        }
        
        return CheckIn(
            id: id,
            userId: userId,
            planId: planId,
            weight: weight,
            checkInDate: checkInDate,
            photoUrl: photoUrl,
            note: note,
            reviewStatus: reviewStatus,
            reviewerId: nil,
            reviewComment: nil,
            createdAt: checkInDate
        )
    }
}

extension OfflineCheckInEntity {
    func toCheckIn() -> CheckIn {
        return CheckIn(
            id: id,
            userId: userId,
            planId: planId,
            weight: weight,
            checkInDate: createdAt,
            photoUrl: photoUrl,
            note: note,
            reviewStatus: .pending,
            reviewerId: nil,
            reviewComment: nil,
            createdAt: createdAt
        )
    }
}