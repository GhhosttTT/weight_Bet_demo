import Foundation
import CoreData

extension OfflineCheckInEntity {

    @nonobjc public class func fetchRequest() -> NSFetchRequest<OfflineCheckInEntity> {
        return NSFetchRequest<OfflineCheckInEntity>(entityName: "OfflineCheckInEntity")
    }

    @NSManaged public var createdAt: Date
    @NSManaged public var id: String
    @NSManaged public var note: String?
    @NSManaged public var photoUrl: String?
    @NSManaged public var planId: String
    @NSManaged public var synced: Bool
    @NSManaged public var userId: String
    @NSManaged public var weight: Double

}
