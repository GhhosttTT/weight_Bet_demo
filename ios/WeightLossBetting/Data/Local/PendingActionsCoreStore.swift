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

    func fetchPendingNetworkActions() async -> [PendingNetworkAction] {
        return await withCheckedContinuation { (continuation: CheckedContinuation<[PendingNetworkAction], Never>) in
            container.performBackgroundTask { backgroundContext in
                let request = NSFetchRequest<NSManagedObject>(entityName: "PendingNetworkActionEntity")
                request.sortDescriptors = [NSSortDescriptor(key: "createdAt", ascending: true)]
                do {
                    let results: [NSManagedObject] = try backgroundContext.fetch(request)
                    let actions: [PendingNetworkAction] = results.compactMap { obj in
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
                    continuation.resume(returning: actions)
                } catch {
                    print("Error fetching pending actions from CoreStore: \(error)")
                    continuation.resume(returning: [])
                }
            }
        }
    }

    func addPendingNetworkAction(_ action: PendingNetworkAction) async {
        await withCheckedContinuation { continuation in
            container.performBackgroundTask { backgroundContext in
                let entity = NSEntityDescription.insertNewObject(forEntityName: "PendingNetworkActionEntity", into: backgroundContext)
                entity.setValue(action.id, forKey: "id")
                entity.setValue(action.type.rawValue, forKey: "type")
                if let params = action.parameters, let data = try? JSONEncoder().encode(params), let str = String(data: data, encoding: .utf8) {
                    entity.setValue(str, forKey: "parameters")
                } else {
                    entity.setValue(nil, forKey: "parameters")
                }
                entity.setValue(Int32(action.attempt), forKey: "attempt")
                entity.setValue(action.createdAt, forKey: "createdAt")

                self.saveContext(backgroundContext)
                continuation.resume()
            }
        }
    }

    func removePendingNetworkAction(id: String, type: PendingActionType) async {
        await withCheckedContinuation { continuation in
            container.performBackgroundTask { backgroundContext in
                let request = NSFetchRequest<NSManagedObject>(entityName: "PendingNetworkActionEntity")
                request.predicate = NSPredicate(format: "id == %@ AND type == %@", id, type.rawValue)
                do {
                    let results = try backgroundContext.fetch(request)
                    for obj in results { backgroundContext.delete(obj) }
                    self.saveContext(backgroundContext)
                } catch {
                    print("Error removing pending action: \(error)")
                }
                continuation.resume()
            }
        }
    }

    func updateAttempt(for id: String, type: PendingActionType, attempt: Int) async {
        await withCheckedContinuation { continuation in
            container.performBackgroundTask { backgroundContext in
                let request = NSFetchRequest<NSManagedObject>(entityName: "PendingNetworkActionEntity")
                request.predicate = NSPredicate(format: "id == %@ AND type == %@", id, type.rawValue)
                do {
                    let results = try backgroundContext.fetch(request)
                    for obj in results {
                        obj.setValue(Int32(attempt), forKey: "attempt")
                    }
                    self.saveContext(backgroundContext)
                } catch {
                    print("Error updating attempt: \(error)")
                }
                continuation.resume()
            }
        }
    }

    // MARK: - Seen Invitations

    func addSeenInvitation(id: String) async {
        await withCheckedContinuation { continuation in
            container.performBackgroundTask { backgroundContext in
                let entity = NSEntityDescription.insertNewObject(forEntityName: "SeenInvitationEntity", into: backgroundContext)
                entity.setValue(id, forKey: "id")
                entity.setValue(Date(), forKey: "seenAt")
                self.saveContext(backgroundContext)
                continuation.resume()
            }
        }
    }

    func hasSeenInvitation(id: String) async -> Bool {
        return await withCheckedContinuation { continuation in
            container.performBackgroundTask { backgroundContext in
                let request = NSFetchRequest<NSManagedObject>(entityName: "SeenInvitationEntity")
                request.predicate = NSPredicate(format: "id == %@", id)
                do {
                    let count = try backgroundContext.count(for: request)
                    continuation.resume(returning: count > 0)
                } catch {
                    print("Error checking seen invitation: \(error)")
                    continuation.resume(returning: false)
                }
            }
        }
    }

    func removeSeenInvitation(id: String) async {
        await withCheckedContinuation { continuation in
            container.performBackgroundTask { backgroundContext in
                let request = NSFetchRequest<NSManagedObject>(entityName: "SeenInvitationEntity")
                request.predicate = NSPredicate(format: "id == %@", id)
                do {
                    let results = try backgroundContext.fetch(request)
                    for obj in results { backgroundContext.delete(obj) }
                    self.saveContext(backgroundContext)
                } catch {
                    print("Error removing seen invitation: \(error)")
                }
                continuation.resume()
            }
        }
    }

    // MARK: - Migration

    func migrateFromUserDefaults(oldQueueKey: String, oldSeenKey: String) async {
        await withCheckedContinuation { continuation in
            container.performBackgroundTask { backgroundContext in
                // Migrate pending actions
                if let data = UserDefaults.standard.data(forKey: oldQueueKey) {
                    if let arr = try? JSONDecoder().decode([PendingNetworkAction].self, from: data) {
                        for a in arr {
                            // Avoid duplicates
                            let fetchRequest = NSFetchRequest<NSManagedObject>(entityName: "PendingNetworkActionEntity")
                            fetchRequest.predicate = NSPredicate(format: "id == %@ AND type == %@", a.id, a.type.rawValue)
                            if (try? backgroundContext.count(for: fetchRequest)) ?? 0 == 0 {
                                let entity = NSEntityDescription.insertNewObject(forEntityName: "PendingNetworkActionEntity", into: backgroundContext)
                                entity.setValue(a.id, forKey: "id")
                                entity.setValue(a.type.rawValue, forKey: "type")
                                if let params = a.parameters, let data = try? JSONEncoder().encode(params), let str = String(data: data, encoding: .utf8) {
                                    entity.setValue(str, forKey: "parameters")
                                } else {
                                    entity.setValue(nil, forKey: "parameters")
                                }
                                entity.setValue(Int32(a.attempt), forKey: "attempt")
                                entity.setValue(a.createdAt, forKey: "createdAt")
                            }
                        }
                        UserDefaults.standard.removeObject(forKey: oldQueueKey)
                    }
                }

                // Migrate seen invitations
                if let seen = UserDefaults.standard.array(forKey: oldSeenKey) as? [String] {
                    for id in seen {
                        let fetchRequest = NSFetchRequest<NSManagedObject>(entityName: "SeenInvitationEntity")
                        fetchRequest.predicate = NSPredicate(format: "id == %@", id)
                        if (try? backgroundContext.count(for: fetchRequest)) ?? 0 == 0 {
                            let entity = NSEntityDescription.insertNewObject(forEntityName: "SeenInvitationEntity", into: backgroundContext)
                            entity.setValue(id, forKey: "id")
                            entity.setValue(Date(), forKey: "seenAt")
                        }
                    }
                    UserDefaults.standard.removeObject(forKey: oldSeenKey)
                }

                self.saveContext(backgroundContext)
                continuation.resume()
            }
        }
    }

    private func saveContext(_ context: NSManagedObjectContext) {
        if context.hasChanges {
            do {
                try context.save()
            } catch {
                print("Failed to save PendingActionsCoreStore context: \(error)")
            }
        }
    }
}

