import Foundation
import CoreData

final class PendingActionsCoreStore {
    static let shared = PendingActionsCoreStore()

    private let container: NSPersistentContainer
    private let modelName = "PendingActionsStore"

    private init() {
        // Programmatically create model with two entities
        let model = NSManagedObjectModel()

        // PendingNetworkActionEntity
        let pendingEntity = NSEntityDescription()
        pendingEntity.name = "PendingNetworkActionEntity"
        pendingEntity.managedObjectClassName = "NSManagedObject"

        var attributes: [String: NSAttributeDescription] = [:]

        let idAttr = NSAttributeDescription()
        idAttr.name = "id"
        idAttr.attributeType = .stringAttributeType
        idAttr.isOptional = false
        attributes["id"] = idAttr

        let typeAttr = NSAttributeDescription()
        typeAttr.name = "type"
        typeAttr.attributeType = .stringAttributeType
        typeAttr.isOptional = false
        attributes["type"] = typeAttr

        let paramsAttr = NSAttributeDescription()
        paramsAttr.name = "parameters"
        paramsAttr.attributeType = .stringAttributeType
        paramsAttr.isOptional = true
        attributes["parameters"] = paramsAttr

        let attemptAttr = NSAttributeDescription()
        attemptAttr.name = "attempt"
        attemptAttr.attributeType = .integer32AttributeType
        attemptAttr.isOptional = false
        attributes["attempt"] = attemptAttr

        let createdAtAttr = NSAttributeDescription()
        createdAtAttr.name = "createdAt"
        createdAtAttr.attributeType = .dateAttributeType
        createdAtAttr.isOptional = false
        attributes["createdAt"] = createdAtAttr

        pendingEntity.properties = Array(attributes.values)

        // SeenInvitationEntity
        let seenEntity = NSEntityDescription()
        seenEntity.name = "SeenInvitationEntity"
        seenEntity.managedObjectClassName = "NSManagedObject"

        let seenIdAttr = NSAttributeDescription()
        seenIdAttr.name = "id"
        seenIdAttr.attributeType = .stringAttributeType
        seenIdAttr.isOptional = false

        let seenAtAttr = NSAttributeDescription()
        seenAtAttr.name = "seenAt"
        seenAtAttr.attributeType = .dateAttributeType
        seenAtAttr.isOptional = false

        seenEntity.properties = [seenIdAttr, seenAtAttr]

        model.entities = [pendingEntity, seenEntity]

        container = NSPersistentContainer(name: modelName, managedObjectModel: model)

        // Store in Application Support directory to avoid conflicts
        let storeURL = FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask).first!
            .appendingPathComponent("PendingActionsStore.sqlite")
        let description = NSPersistentStoreDescription(url: storeURL)
        description.shouldMigrateStoreAutomatically = true
        description.shouldInferMappingModelAutomatically = true
        container.persistentStoreDescriptions = [description]

        container.loadPersistentStores { desc, error in
            if let error = error {
                print("Failed to load PendingActions store: \(error)")
            }
        }
    }

    private var context: NSManagedObjectContext { container.viewContext }

    // MARK: - Pending Actions

    func fetchPendingNetworkActions() -> [PendingNetworkAction] {
        let request = NSFetchRequest<NSManagedObject>(entityName: "PendingNetworkActionEntity")
        request.sortDescriptors = [NSSortDescriptor(key: "createdAt", ascending: true)]
        do {
            let results = try context.fetch(request)
            return results.compactMap { obj in
                guard let id = obj.value(forKey: "id") as? String,
                      let type = obj.value(forKey: "type") as? String,
                      let attempt = obj.value(forKey: "attempt") as? Int32,
                      let createdAt = obj.value(forKey: "createdAt") as? Date else {
                    return nil
                }
                var params: [String: String]? = nil
                if let paramsStr = obj.value(forKey: "parameters") as? String, !paramsStr.isEmpty {
                    if let data = paramsStr.data(using: .utf8),
                       let dict = try? JSONDecoder().decode([String: String].self, from: data) {
                        params = dict
                    }
                }
                return PendingNetworkAction(id: id, type: PendingActionType(rawValue: type) ?? .markSeen, parameters: params, attempt: Int(attempt), createdAt: createdAt)
            }
        } catch {
            print("Error fetching pending actions from CoreStore: \(error)")
            return []
        }
    }

    func addPendingNetworkAction(_ action: PendingNetworkAction) {
        let entity = NSEntityDescription.insertNewObject(forEntityName: "PendingNetworkActionEntity", into: context)
        entity.setValue(action.id, forKey: "id")
        entity.setValue(action.type.rawValue, forKey: "type")
        if let params = action.parameters, let data = try? JSONEncoder().encode(params), let str = String(data: data, encoding: .utf8) {
            entity.setValue(str, forKey: "parameters")
        } else {
            entity.setValue(nil, forKey: "parameters")
        }
        entity.setValue(Int32(action.attempt), forKey: "attempt")
        entity.setValue(action.createdAt, forKey: "createdAt")

        saveContext()
    }

    func removePendingNetworkAction(id: String, type: PendingActionType) {
        let request = NSFetchRequest<NSManagedObject>(entityName: "PendingNetworkActionEntity")
        request.predicate = NSPredicate(format: "id == %@ AND type == %@", id, type.rawValue)
        do {
            let results = try context.fetch(request)
            for obj in results { context.delete(obj) }
            saveContext()
        } catch {
            print("Error removing pending action: \(error)")
        }
    }

    func updateAttempt(for id: String, type: PendingActionType, attempt: Int) {
        let request = NSFetchRequest<NSManagedObject>(entityName: "PendingNetworkActionEntity")
        request.predicate = NSPredicate(format: "id == %@ AND type == %@", id, type.rawValue)
        do {
            let results = try context.fetch(request)
            for obj in results {
                obj.setValue(Int32(attempt), forKey: "attempt")
            }
            saveContext()
        } catch {
            print("Error updating attempt: \(error)")
        }
    }

    // MARK: - Seen Invitations

    func addSeenInvitation(id: String) {
        let entity = NSEntityDescription.insertNewObject(forEntityName: "SeenInvitationEntity", into: context)
        entity.setValue(id, forKey: "id")
        entity.setValue(Date(), forKey: "seenAt")
        saveContext()
    }

    func hasSeenInvitation(id: String) -> Bool {
        let request = NSFetchRequest<NSManagedObject>(entityName: "SeenInvitationEntity")
        request.predicate = NSPredicate(format: "id == %@", id)
        do {
            let count = try context.count(for: request)
            return count > 0
        } catch {
            print("Error checking seen invitation: \(error)")
            return false
        }
    }

    func removeSeenInvitation(id: String) {
        let request = NSFetchRequest<NSManagedObject>(entityName: "SeenInvitationEntity")
        request.predicate = NSPredicate(format: "id == %@", id)
        do {
            let results = try context.fetch(request)
            for obj in results { context.delete(obj) }
            saveContext()
        } catch {
            print("Error removing seen invitation: \(error)")
        }
    }

    // MARK: - Migration

    func migrateFromUserDefaults(oldQueueKey: String, oldSeenKey: String) {
        // Migrate pending actions
        if let data = UserDefaults.standard.data(forKey: oldQueueKey) {
            if let arr = try? JSONDecoder().decode([PendingNetworkAction].self, from: data) {
                for a in arr {
                    // Avoid duplicates
                    if !fetchPendingNetworkActions().contains(where: { $0.id == a.id && $0.type == a.type }) {
                        addPendingNetworkAction(a)
                    }
                }
                UserDefaults.standard.removeObject(forKey: oldQueueKey)
            }
        }

        // Migrate seen invitations
        if let seen = UserDefaults.standard.array(forKey: oldSeenKey) as? [String] {
            for id in seen {
                if !hasSeenInvitation(id: id) {
                    addSeenInvitation(id: id)
                }
            }
            UserDefaults.standard.removeObject(forKey: oldSeenKey)
        }
    }

    private func saveContext() {
        if context.hasChanges {
            do {
                try context.save()
            } catch {
                print("Failed to save PendingActionsCoreStore context: \(error)")
            }
        }
    }
}

