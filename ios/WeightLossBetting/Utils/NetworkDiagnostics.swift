import Foundation

class NetworkDiagnostics {
    static let shared = NetworkDiagnostics()
    
    private init() {}
    
    /// 检查服务器连接状态
    func checkServerConnection(baseURL: String, completion: @escaping (Bool, String) -> Void) {
        guard let url = URL(string: baseURL) else {
            completion(false, "❌ 无效的服务器地址: \(baseURL)")
            return
        }
        
        print("🔍 开始检查服务器连接...")
        print("   目标地址: \(baseURL)")
        
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        request.timeoutInterval = 5
        
        let task = URLSession.shared.dataTask(with: request) { data, response, error in
            if let error = error {
                let errorMessage = """
                ❌ 无法连接到服务器
                错误: \(error.localizedDescription)
                
                可能的原因：
                1. 后端服务未启动
                2. 防火墙阻止了连接
                3. IP 地址或端口错误
                4. 设备不在同一网络
                """
                completion(false, errorMessage)
                return
            }
            
            if let httpResponse = response as? HTTPURLResponse {
                let statusCode = httpResponse.statusCode
                let message = """
                ✅ 服务器可访问
                状态码: \(statusCode)
                服务器: \(httpResponse.url?.absoluteString ?? "unknown")
                """
                completion(true, message)
            } else {
                completion(false, "❌ 收到无效的响应")
            }
        }
        
        task.resume()
    }
    
    /// 测试登录端点
    func testLoginEndpoint(baseURL: String, completion: @escaping (Bool, String) -> Void) {
        let loginURL = "\(baseURL)/auth/login"
        guard let url = URL(string: loginURL) else {
            completion(false, "❌ 无效的登录地址: \(loginURL)")
            return
        }
        
        print("🔍 测试登录端点...")
        print("   目标地址: \(loginURL)")
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.timeoutInterval = 10
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        // 发送空请求来测试端点是否存在
        let testData = ["email": "test@test.com", "password": "test"]
        request.httpBody = try? JSONSerialization.data(withJSONObject: testData)
        
        let task = URLSession.shared.dataTask(with: request) { data, response, error in
            if let error = error {
                let errorMessage = """
                ❌ 登录端点测试失败
                错误: \(error.localizedDescription)
                """
                completion(false, errorMessage)
                return
            }
            
            if let httpResponse = response as? HTTPURLResponse {
                let statusCode = httpResponse.statusCode
                var message = "登录端点响应: \(statusCode)\n"
                
                if let data = data, let responseString = String(data: data, encoding: .utf8) {
                    message += "响应内容: \(responseString)"
                }
                
                // 400/401/422 都说明端点存在，只是认证失败
                if statusCode == 502 || statusCode == 503 || statusCode == 504 {
                    message = "❌ 服务器错误 (\(statusCode))\n后端服务可能未正常运行"
                    completion(false, message)
                } else {
                    message = "✅ 登录端点可访问 (状态码: \(statusCode))\n" + message
                    completion(true, message)
                }
            }
        }
        
        task.resume()
    }
    
    /// 完整的网络诊断
    func runFullDiagnostics(baseURL: String, completion: @escaping (String) -> Void) {
        var diagnosticReport = "📊 网络诊断报告\n"
        diagnosticReport += "==================\n\n"
        diagnosticReport += "服务器地址: \(baseURL)\n\n"
        
        // 1. 检查基础连接
        checkServerConnection(baseURL: baseURL) { success, message in
            diagnosticReport += "1️⃣ 基础连接测试:\n\(message)\n\n"
            
            if success {
                // 2. 测试登录端点
                self.testLoginEndpoint(baseURL: baseURL) { success, message in
                    diagnosticReport += "2️⃣ 登录端点测试:\n\(message)\n\n"
                    
                    if !success {
                        diagnosticReport += """
                        
                        🔧 建议的解决步骤：
                        1. 确认后端服务正在运行
                        2. 检查后端日志是否有错误
                        3. 验证 IP 地址和端口是否正确
                        4. 确保设备在同一网络（如果使用局域网 IP）
                        5. 尝试在浏览器访问: \(baseURL)
                        """
                    }
                    
                    completion(diagnosticReport)
                }
            } else {
                diagnosticReport += """
                
                🔧 建议的解决步骤：
                1. 检查后端服务是否启动
                2. 验证 IP 地址: 192.168.1.10
                3. 验证端口: 8000
                4. 确保设备连接到同一 WiFi 网络
                5. 检查防火墙设置
                6. 尝试 ping 192.168.1.10
                """
                
                completion(diagnosticReport)
            }
        }
    }
}
