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
        let entity = UserEntity(context: context)
        entity.id = user.id
        entity.email = user.email
        entity.nickname = user.nickname
        entity.gender = user.gender.rawValue
        entity.age = Int16(user.age)
        entity.height = user.height
        entity.currentWeight = user.currentWeight
        entity.targetWeight = user.targetWeight ?? 0
        entity.updatedAt = Date()
        
        saveContext()
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
        // Check if plan already exists
        let fetchRequest: NSFetchRequest<BettingPlanEntity> = BettingPlanEntity.fetchRequest()
        fetchRequest.predicate = NSPredicate(format: "id == %@", plan.id)
        
        do {
            let results = try context.fetch(fetchRequest)
            let entity = results.first ?? BettingPlanEntity(context: context)
            
            entity.id = plan.id
            entity.creatorId = plan.creatorId
            entity.participantId = plan.participantId
            entity.status = plan.status.rawValue
            entity.betAmount = plan.betAmount
            entity.startDate = plan.startDate
            entity.endDate = plan.endDate
            entity.planDescription = plan.description
            entity.updatedAt = Date()
            
            // Encode Goal data to binary
            if let creatorGoalData = try? JSONEncoder().encode(plan.creatorGoal) {
                entity.creatorGoalData = creatorGoalData
            }
            
            if let participantGoal = plan.participantGoal,
               let participantGoalData = try? JSONEncoder().encode(participantGoal) {
                entity.participantGoalData = participantGoalData
            }
            
            saveContext()
        } catch {
            print("Error caching betting plan: \(error)")
        }
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
        let entity = CheckInEntity(context: context)
        entity.id = checkIn.id
        entity.userId = checkIn.userId
        entity.planId = checkIn.planId
        entity.weight = checkIn.weight
        entity.checkInDate = checkIn.checkInDate
        entity.photoUrl = checkIn.photoUrl
        entity.note = checkIn.note
        entity.reviewStatus = checkIn.reviewStatus.rawValue
        
        saveContext()
    }
    
    func getCachedCheckIns(planId: String) -> [CheckIn] {
        let fetchRequest: NSFetchRequest<CheckInEntity> = CheckInEntity.fetchRequest()
        fetchRequest.predicate = NSPredicate(format: "planId == %@", planId)
        fetchRequest.sortDescriptors = [NSSortDescriptor(key: "checkInDate", ascending: false)]
        
        do {
            let results = try context.fetch(fetchRequest)
            return results.compactMap { entity in
                guard let reviewStatus = ReviewStatus(rawValue: entity.reviewStatus) else {
                    return nil
                }
                
                return CheckIn(
                    id: entity.id,
                    userId: entity.userId,
                    planId: entity.planId,
                    weight: entity.weight,
                    checkInDate: entity.checkInDate,
                    photoUrl: entity.photoUrl,
                    note: entity.note,
                    reviewStatus: reviewStatus,
                    reviewerId: nil,
                    reviewComment: nil,
                    createdAt: entity.checkInDate
                )
            }
        } catch {
            print("Error fetching cached check-ins: \(error)")
            return []
        }
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
            phoneNumber: nil,
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
        
        // Decode Goal data from binary
        var creatorGoal = Goal(initialWeight: 0, targetWeight: 0, targetWeightLoss: 0)
        if let creatorGoalData = creatorGoalData,
           let decoded = try? JSONDecoder().decode(Goal.self, from: creatorGoalData) {
            creatorGoal = decoded
        }
        
        var participantGoal: Goal? = nil
        if let participantGoalData = participantGoalData,
           let decoded = try? JSONDecoder().decode(Goal.self, from: participantGoalData) {
            participantGoal = decoded
        }
        
        return BettingPlan(
            id: id,
            creatorId: creatorId,
            participantId: participantId,
            status: status,
            betAmount: betAmount,
            startDate: startDate,
            endDate: endDate,
            description: planDescription,
            creatorGoal: creatorGoal,
            participantGoal: participantGoal,
            createdAt: Date(),
            activatedAt: nil
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