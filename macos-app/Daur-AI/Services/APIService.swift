import Foundation

class APIService {
    static let shared = APIService()
    
    private var baseURL: URL?
    private var session: URLSession
    private var authToken: String?
    
    init() {
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = 10
        config.timeoutIntervalForResource = 30
        self.session = URLSession(configuration: config)
    }
    
    // MARK: - Connection Management
    func connect(host: String, port: Int) {
        self.baseURL = URL(string: "http://\(host):\(port)")
        checkConnection()
    }
    
    func disconnect() {
        self.baseURL = nil
        self.authToken = nil
        session.invalidateAndCancel()
    }
    
    private func checkConnection() {
        guard let baseURL = baseURL else { return }
        
        let url = baseURL.appendingPathComponent("health")
        var request = URLRequest(url: url)
        request.timeoutInterval = 5
        
        session.dataTask(with: request) { data, response, error in
            if let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200 {
                print("✅ Connected to Daur-AI API")
            } else {
                print("❌ Failed to connect to Daur-AI API")
            }
        }.resume()
    }
    
    // MARK: - System Information
    func getSystemInfo(completion: @escaping (Result<[String: Any], Error>) -> Void) {
        guard let baseURL = baseURL else {
            completion(.failure(APIError.notConnected))
            return
        }
        
        let url = baseURL.appendingPathComponent("system/info")
        performRequest(url: url, completion: completion)
    }
    
    // MARK: - Hardware Monitoring
    func getCPUMetrics(completion: @escaping (Result<CPUMetrics, Error>) -> Void) {
        guard let baseURL = baseURL else {
            completion(.failure(APIError.notConnected))
            return
        }
        
        let url = baseURL.appendingPathComponent("hardware/cpu")
        performRequest(url: url) { (result: Result<[String: Double], Error>) in
            switch result {
            case .success(let data):
                let metrics = CPUMetrics(
                    percent: data["percent"] ?? 0,
                    count: Int(data["count"] ?? 0),
                    freq: data["freq"] ?? 0
                )
                completion(.success(metrics))
            case .failure(let error):
                completion(.failure(error))
            }
        }
    }
    
    func getMemoryMetrics(completion: @escaping (Result<MemoryMetrics, Error>) -> Void) {
        guard let baseURL = baseURL else {
            completion(.failure(APIError.notConnected))
            return
        }
        
        let url = baseURL.appendingPathComponent("hardware/memory")
        performRequest(url: url) { (result: Result<[String: Double], Error>) in
            switch result {
            case .success(let data):
                let metrics = MemoryMetrics(
                    total: Int(data["total"] ?? 0),
                    available: Int(data["available"] ?? 0),
                    percent: data["percent"] ?? 0
                )
                completion(.success(metrics))
            case .failure(let error):
                completion(.failure(error))
            }
        }
    }
    
    func getDiskMetrics(completion: @escaping (Result<DiskMetrics, Error>) -> Void) {
        guard let baseURL = baseURL else {
            completion(.failure(APIError.notConnected))
            return
        }
        
        let url = baseURL.appendingPathComponent("hardware/disk")
        performRequest(url: url) { (result: Result<[String: Double], Error>) in
            switch result {
            case .success(let data):
                let metrics = DiskMetrics(
                    total: Int(data["total"] ?? 0),
                    free: Int(data["free"] ?? 0),
                    percent: data["percent"] ?? 0
                )
                completion(.success(metrics))
            case .failure(let error):
                completion(.failure(error))
            }
        }
    }
    
    // MARK: - Authentication
    func register(username: String, email: String, password: String, 
                  completion: @escaping (Result<[String: Any], Error>) -> Void) {
        guard let baseURL = baseURL else {
            completion(.failure(APIError.notConnected))
            return
        }
        
        let url = baseURL.appendingPathComponent("auth/register")
        let body: [String: Any] = [
            "username": username,
            "email": email,
            "password": password
        ]
        
        performPOSTRequest(url: url, body: body, completion: completion)
    }
    
    func login(username: String, password: String,
               completion: @escaping (Result<LoginResponse, Error>) -> Void) {
        guard let baseURL = baseURL else {
            completion(.failure(APIError.notConnected))
            return
        }
        
        let url = baseURL.appendingPathComponent("auth/login")
        let body: [String: Any] = [
            "username": username,
            "password": password
        ]
        
        performPOSTRequest(url: url, body: body) { (result: Result<[String: Any], Error>) in
            switch result {
            case .success(let data):
                if let token = data["access_token"] as? String {
                    self.authToken = token
                    let response = LoginResponse(
                        message: data["message"] as? String ?? "",
                        accessToken: token,
                        tokenType: data["token_type"] as? String ?? "Bearer"
                    )
                    completion(.success(response))
                } else {
                    completion(.failure(APIError.invalidResponse))
                }
            case .failure(let error):
                completion(.failure(error))
            }
        }
    }
    
    // MARK: - Helper Methods
    private func performRequest<T: Decodable>(url: URL, 
                                             completion: @escaping (Result<T, Error>) -> Void) {
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        
        if let token = authToken {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
        
        session.dataTask(with: request) { data, response, error in
            if let error = error {
                completion(.failure(error))
                return
            }
            
            guard let data = data else {
                completion(.failure(APIError.noData))
                return
            }
            
            do {
                let decoder = JSONDecoder()
                let result = try decoder.decode(T.self, from: data)
                completion(.success(result))
            } catch {
                completion(.failure(error))
            }
        }.resume()
    }
    
    private func performPOSTRequest<T: Decodable>(url: URL, body: [String: Any],
                                                  completion: @escaping (Result<T, Error>) -> Void) {
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        if let token = authToken {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
        
        do {
            request.httpBody = try JSONSerialization.data(withJSONObject: body)
        } catch {
            completion(.failure(error))
            return
        }
        
        session.dataTask(with: request) { data, response, error in
            if let error = error {
                completion(.failure(error))
                return
            }
            
            guard let data = data else {
                completion(.failure(APIError.noData))
                return
            }
            
            do {
                let decoder = JSONDecoder()
                let result = try decoder.decode(T.self, from: data)
                completion(.success(result))
            } catch {
                completion(.failure(error))
            }
        }.resume()
    }
}

// MARK: - Models
struct CPUMetrics {
    let percent: Double
    let count: Int
    let freq: Double
}

struct MemoryMetrics {
    let total: Int
    let available: Int
    let percent: Double
}

struct DiskMetrics {
    let total: Int
    let free: Int
    let percent: Double
}

struct LoginResponse: Decodable {
    let message: String
    let accessToken: String
    let tokenType: String
    
    enum CodingKeys: String, CodingKey {
        case message
        case accessToken = "access_token"
        case tokenType = "token_type"
    }
}

// MARK: - Error Handling
enum APIError: Error {
    case notConnected
    case noData
    case invalidResponse
    case decodingError
}

