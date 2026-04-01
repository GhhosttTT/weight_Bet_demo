import Foundation
import CoreData

extension UserEntity {

    @nonobjc public class func fetchRequest() -> NSFetchRequest<UserEntity> {
        return NSFetchRequest<UserEntity>(entityName: "UserEntity")
    }

    @NSManaged public var age: Int16
    @NSManaged public var currentWeight: Double
    @NSManaged public var email: String
    @NSManaged public var gender: String
    @NSManaged public var height: Double
    @NSManaged public var id: String
    @NSManaged public var nickname: String
    @NSManaged public var targetWeight: Double
    @NSManaged public var updatedAt: Date?

}

// MARK: Generated accessors for relationships

extension UserEntity {

    @objc(addBettingPlanEntitiesObject:)
    @NSManaged public func addToBettingPlanEntities(_ value: BettingPlanEntity)

    @objc(removeBettingPlanEntitiesObject:)
    @NSManaged public func removeFromBettingPlanEntities(_ value: BettingPlanEntity)

    @objc(addBettingPlanEntities:)
    @NSManaged public func addToBettingPlanEntities(_ values: Set<BettingPlanEntity>)

    @objc(removeBettingPlanEntities:)
    @NSManaged public func removeFromBettingPlanEntities(_ values: Set<BettingPlanEntity>)

}
