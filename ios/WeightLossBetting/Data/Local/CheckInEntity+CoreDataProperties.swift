import Foundation
import CoreData

extension CheckInEntity {

    @nonobjc public class func fetchRequest() -> NSFetchRequest<CheckInEntity> {
        return NSFetchRequest<CheckInEntity>(entityName: "CheckInEntity")
    }

    @NSManaged public var checkInDate: Date
    @NSManaged public var id: String
    @NSManaged public var note: String?
    @NSManaged public var photoUrl: String?
    @NSManaged public var planId: String
    @NSManaged public var reviewStatus: String
    @NSManaged public var userId: String
    @NSManaged public var weight: Double

}

// MARK: Generated accessors for relationships

extension CheckInEntity {

}
