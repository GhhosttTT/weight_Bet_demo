import Foundation
import CoreData

extension BettingPlanEntity {

    @nonobjc public class func fetchRequest() -> NSFetchRequest<BettingPlanEntity> {
        return NSFetchRequest<BettingPlanEntity>(entityName: "BettingPlanEntity")
    }

    @NSManaged public var betAmount: Double
    @NSManaged public var creatorGoalData: Data?
    @NSManaged public var creatorId: String
    @NSManaged public var endDate: Date
    @NSManaged public var id: String
    @NSManaged public var participantGoalData: Data?
    @NSManaged public var participantId: String?
    @NSManaged public var planDescription: String?
    @NSManaged public var startDate: Date
    @NSManaged public var status: String
    @NSManaged public var updatedAt: Date?

}

// MARK: Generated accessors for relationships

extension BettingPlanEntity {

}
