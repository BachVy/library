import json
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Union
from fuzzywuzzy import fuzz

class DocumentManager:
    def __init__(self, documents_file: str, requests_file: str = "document_requests.json", 
                 log_file: str = "document_logs.json", categories_file: str = "document_categories.json",
                 ratings_file: str = "document_ratings.json"):
        self.documents_file = documents_file
        self.requests_file = requests_file
        self.log_file = log_file
        self.categories_file = categories_file
        self.ratings_file = ratings_file
        self.documents = self._load_documents()
        self.requests = self._load_requests()
        self.logs = self._load_logs()
        self.categories = self._load_categories()
        self.ratings = self._load_ratings()

    def _load_documents(self) -> List[Dict]:
        try:
            with open(self.documents_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def _load_requests(self) -> List[Dict]:
        try:
            with open(self.requests_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def _load_logs(self) -> List[Dict]:
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def _load_categories(self) -> List[Dict]:
        try:
            with open(self.categories_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # Danh mục mặc định nếu file không tồn tại
            default_categories = [
                {"category_id": "DM001", "name": "SÁCH GIÁO KHOA", "description": "Sách giáo khoa các cấp"},
                {"category_id": "DM002", "name": "TIỂU THUYẾT", "description": "Các thể loại tiểu thuyết"},
                {"category_id": "DM003", "name": "TÀI LIỆU THAM KHẢO", "description": "Tài liệu nghiên cứu, tham khảo"}
            ]
            self._save_categories(default_categories)
            return default_categories

    def _load_ratings(self) -> List[Dict]:
        try:
            with open(self.ratings_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def _save_documents(self):
        with open(self.documents_file, 'w', encoding='utf-8') as f:
            json.dump(self.documents, f, ensure_ascii=False, indent=4)

    def _save_requests(self):
        with open(self.requests_file, 'w', encoding='utf-8') as f:
            json.dump(self.requests, f, ensure_ascii=False, indent=4)

    def _save_logs(self):
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(self.logs, f, ensure_ascii=False, indent=4)

    def _save_categories(self, categories: List[Dict]):
        with open(self.categories_file, 'w', encoding='utf-8') as f:
            json.dump(categories, f, ensure_ascii=False, indent=4)

    def _save_ratings(self):
        with open(self.ratings_file, 'w', encoding='utf-8') as f:
            json.dump(self.ratings, f, ensure_ascii=False, indent=4)

    def _log_action(self, action: str, doc_id: str, details: str):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "doc_id": doc_id,
            "details": details
        }
        self.logs.append(log_entry)
        self._save_logs()

    def _generate_doc_id(self) -> str:
        return f"TL{str(len(self.documents) + 1).zfill(3)}"

    def _generate_category_id(self) -> str:
        return f"DM{str(len(self.categories) + 1).zfill(3)}"

    def _check_duplicate_doc_id(self, doc_id: str) -> bool:
        return any(doc['doc_id'] == doc_id for doc in self.documents)

    def _check_duplicate_category_name(self, name: str) -> bool:
        return any(cat['name'].upper() == name.upper() for cat in self.categories)

    def _update_status(self, document: Dict):
        """Cập nhật trạng thái tài liệu dựa trên AvailableQuantity."""
        if document['AvailableQuantity'] > 0:
            document['status'] = "available"
        else:
            document['status'] = "unavailable"

    def add_document(self, title: str, category: str, SoLuong: int, DacBiet: bool = False) -> Dict:
        if not title or not category:
            raise ValueError("Tên tài liệu và lĩnh vực không được để trống")
        if SoLuong < 0:
            raise ValueError("Số lượng không được âm")

        doc_id = self._generate_doc_id()
        if self._check_duplicate_doc_id(doc_id):
            raise ValueError("Mã tài liệu đã tồn tại")

        document = {
            "doc_id": doc_id,
            "title": title.upper(),
            "category": category.upper(),
            "SoLuong": SoLuong,
            "DacBiet": DacBiet,
            "status": "available" if SoLuong > 0 else "unavailable",
            "AvailableQuantity": SoLuong
        }
        self.documents.append(document)
        self._save_documents()
        self._log_action("add", doc_id, f"Thêm tài liệu: {title}")
        return document

    def search_documents(self, doc_id: Optional[str] = None, title: Optional[str] = None, 
                        category: Optional[str] = None, min_similarity: int = 80) -> List[Dict]:
        results = []
        for doc in self.documents:
            match = True
            if doc_id and doc_id.lower() not in doc['doc_id'].lower():
                match = False
            if title:
                similarity = fuzz.partial_ratio(title.lower(), doc['title'].lower())
                if similarity < min_similarity:
                    match = False
            if category and category.lower() not in doc['category'].lower():
                match = False
            if match:
                results.append({
                    "stt": len(results) + 1,
                    "doc_id": doc['doc_id'],
                    "title": doc['title'],
                    "category": doc['category'],
                    "SoLuong": doc['SoLuong'],
                    "DacBiet": doc['DacBiet'],
                    "status": doc['status'],
                    "AvailableQuantity": doc['AvailableQuantity']
                })
        return results
    # thay 
    def update_document(self, doc_id: str, updates: Dict) -> bool:
        document = self.get_document_details(doc_id)
        if not document:
            self._log_action("update_document", doc_id, f"Không tìm thấy tài liệu để cập nhật: {doc_id}")
            return False

        if 'doc_id' in updates:
            raise ValueError("Không thể chỉnh sửa mã tài liệu")

        # Kiểm tra nếu tài liệu đang được mượn và có thay đổi số lượng
        if ('SoLuong' in updates or 'AvailableQuantity' in updates) and hasattr(self, 'borrowing_manager'):
            if self.borrowing_manager.is_document_borrowed(doc_id):
                raise ValueError("Tài liệu đang được mượn, không thể cập nhật số lượng!")

        valid_fields = ['title', 'category', 'SoLuong', 'DacBiet', 'AvailableQuantity']
        for key, value in updates.items():
            if key not in valid_fields:
                raise ValueError(f"Trường {key} không hợp lệ")
            if key in ['title', 'category']:
                # Kiểm tra giá trị không chỉ chứa khoảng trắng
                if not value or value.isspace():
                    raise ValueError(f"Trường {key} không được để trống hoặc chỉ chứa khoảng trắng")
                # Kiểm tra độ dài tối đa cho title (ví dụ: 200 ký tự)
                if key == 'title' and len(value) > 200:
                    raise ValueError("Tiêu đề không được dài quá 200 ký tự")
            if key in ['SoLuong', 'AvailableQuantity'] and value < 0:
                raise ValueError("Số lượng không được âm")

            if key == 'SoLuong':
                document[key] = value
                if 'AvailableQuantity' not in updates:
                    document['AvailableQuantity'] = value
            elif key == 'AvailableQuantity':
                document[key] = value
            elif key == 'title':
                # Giữ nguyên định dạng tự nhiên của tiêu đề
                document[key] = value.strip()
            elif key == 'category':
                # Chuẩn hóa category thành chữ hoa
                document[key] = value.upper().strip()
            else:
                document[key] = value

        # Cập nhật trạng thái dựa trên AvailableQuantity
        self._update_status(document)

        # Ghi log chi tiết các thay đổi
        changes = ", ".join(f"{key}: {value}" for key, value in updates.items())
        self._log_action("update", doc_id, f"Cập nhật tài liệu: {document['title']} - Thay đổi: {changes}")

        self._save_documents()
        return True
    #thay doi
    def delete_document(self, doc_id: str) -> bool:
        document = self.get_document_details(doc_id)
        if not document:
            return False

        if document['status'] == "unavailable" and document['AvailableQuantity'] > 0:
            raise ValueError("Tài liệu đang được mượn, không thể xóa")

        # Đánh dấu tài liệu là đã xóa
        document['deleted'] = True
        self._save_documents()
        self._log_action("delete", doc_id, f"Xóa tài liệu: {document['title']}")
        return True

    def request_document(self, title: str, category: str, reader_id: str):
        if not title or not category:
            raise ValueError("Tên tài liệu và lĩnh vực không được để trống")

        request = {
            "request_id": str(uuid.uuid4()),
            "title": title.upper(),
            "category": category.upper(),
            "reader_id": reader_id,
            "timestamp": datetime.now().isoformat()
        }
        self.requests.append(request)
        self._save_requests()
        self._log_action("request", "", f"Yêu cầu tài liệu mới: {title} bởi độc giả {reader_id}")
        return request

    def get_document_stats(self) -> Dict:
        stats = {
            "by_title": {},
            "by_category": {},
            "by_status": {},
            "by_DacBiet": {}
        }
        for doc in self.documents:
            title = doc['title']
            category = doc['category']
            status = doc['status']
            DacBiet = doc['DacBiet']
            stats['by_title'][title] = stats['by_title'].get(title, 0) + doc['SoLuong']
            stats['by_category'][category] = stats['by_category'].get(category, 0) + doc['SoLuong']
            stats['by_status'][status] = stats['by_status'].get(status, 0) + doc['SoLuong']
            stats['by_DacBiet'][str(DacBiet)] = stats['by_DacBiet'].get(str(DacBiet), 0) + doc['SoLuong']
        return stats

    def get_borrowed_documents_stats(self, readers: List[Dict]) -> Dict:
        stats = {
            "by_title": {},
            "by_category": {}
        }
        doc_dict = {doc['doc_id']: doc for doc in self.documents}
        for reader in readers:
            for record in reader.get('borrow_history', []):
                if record['status'] == 'borrowed':
                    doc_id = record['book_id']
                    doc = doc_dict.get(doc_id)
                    if doc:
                        title = doc['title']
                        category = doc['category']
                        stats['by_title'][title] = stats['by_title'].get(title, 0) + 1
                        stats['by_category'][category] = stats['by_category'].get(category, 0) + 1
        return stats

    def borrow_document(self, doc_id: str) -> bool:
        document = self.get_document_details(doc_id)
        if not document:
            return False
        if document['status'] != "available":
            raise ValueError(f"Tài liệu {doc_id} hiện không có sẵn để mượn")
        if document['AvailableQuantity'] <= 0:
            raise ValueError(f"Tài liệu {doc_id} không còn bản sao nào để mượn")

        document['AvailableQuantity'] -= 1
        self._update_status(document)
        self._save_documents()
        return True

    def return_document(self, doc_id: str) -> bool:
        document = self.get_document_details(doc_id)
        if not document:
            return False
        if document['AvailableQuantity'] >= document['SoLuong']:
            raise ValueError(f"Tài liệu {doc_id} đã đạt số lượng tối đa")

        document['AvailableQuantity'] += 1
        self._update_status(document)
        self._save_documents()
        return True
    def import_documents_from_json(self, file_path: str) -> Dict[str, Union[int, List[str]]]:
        """
        Nhập tài liệu hàng loạt từ file JSON
        Trả về dict với số lượng thành công, thất bại và danh sách lỗi
        """
        result = {
            "success": 0,
            "failed": 0,
            "errors": []
        }

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                documents_to_import = json.load(f)
        except Exception as e:
            result["failed"] += 1
            result["errors"].append(f"Lỗi đọc file: {str(e)}")
            return result

        if not isinstance(documents_to_import, list):
            result["failed"] += 1
            result["errors"].append("Dữ liệu không hợp lệ: phải là mảng các tài liệu")
            return result

        for doc in documents_to_import:
            try:
                # Kiểm tra các trường bắt buộc
                required_fields = ['title', 'category', 'SoLuong']
                for field in required_fields:
                    if field not in doc:
                        raise ValueError(f"Thiếu trường bắt buộc: {field}")

                # Kiểm tra trùng doc_id nếu có
                if 'doc_id' in doc and self._check_duplicate_doc_id(doc['doc_id']):
                    raise ValueError(f"doc_id '{doc['doc_id']}' đã tồn tại")

                # Tạo doc_id mới nếu không có
                if 'doc_id' not in doc:
                    doc['doc_id'] = self._generate_doc_id()

                # Chuẩn hóa dữ liệu
                doc['title'] = doc['title'].upper()
                doc['category'] = doc['category'].upper()
                doc['DacBiet'] = doc.get('DacBiet', False)
                doc['AvailableQuantity'] = doc['SoLuong']
                doc['status'] = "available" if doc['SoLuong'] > 0 else "unavailable"

                self.documents.append(doc)
                result["success"] += 1
                self._log_action("import", doc['doc_id'], f"Nhập tài liệu từ file: {doc['title']}")

            except Exception as e:
                result["failed"] += 1
                result["errors"].append(f"Lỗi với tài liệu {doc.get('title', 'Không rõ')}: {str(e)}")

        if result["success"] > 0:
            self._save_documents()

        return result

    def add_category(self, name: str, description: str = "") -> Dict:
        """
        Thêm danh mục mới
        """
        if not name:
            raise ValueError("Tên danh mục không được để trống")

        if self._check_duplicate_category_name(name):
            raise ValueError(f"Danh mục '{name}' đã tồn tại")

        category = {
            "category_id": self._generate_category_id(),
            "name": name.upper(),
            "description": description
        }

        self.categories.append(category)
        self._save_categories(self.categories)
        self._log_action("add_category", "", f"Thêm danh mục: {name}")
        return category

    def update_category(self, category_id: str, updates: Dict) -> bool:
        """
        Cập nhật thông tin danh mục
        """
        category = next((cat for cat in self.categories if cat['category_id'] == category_id), None)
        if not category:
            return False

        if 'name' in updates:
            new_name = updates['name'].upper()
            if new_name != category['name'] and self._check_duplicate_category_name(new_name):
                raise ValueError(f"Danh mục '{new_name}' đã tồn tại")
            category['name'] = new_name

        if 'description' in updates:
            category['description'] = updates['description']

        self._save_categories(self.categories)
        self._log_action("update_category", "", f"Cập nhật danh mục: {category['name']}")
        return True

    def delete_category(self, category_id: str) -> bool:
        """
        Xóa danh mục
        """
        category = next((cat for cat in self.categories if cat['category_id'] == category_id), None)
        if not category:
            return False

        # Kiểm tra xem danh mục có đang được sử dụng không
        if any(doc['category'] == category['name'] for doc in self.documents):
            raise ValueError("Không thể xóa danh mục đang có tài liệu")

        self.categories = [cat for cat in self.categories if cat['category_id'] != category_id]
        self._save_categories(self.categories)
        self._log_action("delete_category", "", f"Xóa danh mục: {category['name']}")
        return True

    def get_all_categories(self) -> List[Dict]:
        """
        Lấy danh sách tất cả danh mục
        """
        return self.categories

    def add_rating(self, doc_id: str, reader_id: str, rating: int, comment: str = "") -> Dict:
        """
        Thêm đánh giá cho tài liệu (1-5 sao)
        """
        if not 1 <= rating <= 5:
            raise ValueError("Đánh giá phải từ 1 đến 5 sao")

        document = self.get_document_details(doc_id)
        if not document:
            raise ValueError("Tài liệu không tồn tại")

        rating_entry = {
            "rating_id": str(uuid.uuid4()),
            "doc_id": doc_id,
            "reader_id": reader_id,
            "rating": rating,
            "comment": comment,
            "timestamp": datetime.now().isoformat(),
            "approved": False  # Chờ duyệt
        }

        self.ratings.append(rating_entry)
        self._save_ratings()
        self._log_action("add_rating", doc_id, f"Thêm đánh giá {rating} sao cho tài liệu bởi độc giả {reader_id}")
        return rating_entry

    def get_ratings(self, doc_id: Optional[str] = None, approved_only: bool = True) -> List[Dict]:
        """
        Lấy danh sách đánh giá, có thể lọc theo doc_id và trạng thái duyệt
        """
        results = self.ratings
        if doc_id:
            results = [r for r in results if r['doc_id'] == doc_id]
        if approved_only:
            results = [r for r in results if r['approved']]
        return results

    def get_average_rating(self, doc_id: str) -> Optional[float]:
        """
        Tính điểm đánh giá trung bình của tài liệu (chỉ tính các đánh giá đã duyệt)
        """
        ratings = self.get_ratings(doc_id, approved_only=True)
        if not ratings:
            return None
        return sum(r['rating'] for r in ratings) / len(ratings)

    def approve_rating(self, rating_id: str, approve: bool = True) -> bool:
        """
        Duyệt hoặc từ chối đánh giá
        """
        rating = next((r for r in self.ratings if r['rating_id'] == rating_id), None)
        if not rating:
            return False

        rating['approved'] = approve
        self._save_ratings()
        action = "duyệt" if approve else "từ chối"
        self._log_action("approve_rating", rating['doc_id'], f"{action} đánh giá {rating_id}")
        return True

    def approve_document_request(self, request_id: str, approve: bool = True) -> bool:
        """
        Duyệt hoặc từ chối đề xuất tài liệu mới
        """
        request = next((req for req in self.requests if req['request_id'] == request_id), None)
        if not request:
            return False

        if approve:
            # Nếu duyệt, thêm vào danh sách tài liệu
            try:
                self.add_document(
                    title=request['title'],
                    category=request['category'],
                    SoLuong=1  # Mặc định số lượng 1 khi duyệt đề xuất
                )
                action_msg = "Duyệt và thêm tài liệu từ đề xuất"
            except Exception as e:
                raise ValueError(f"Không thể thêm tài liệu từ đề xuất: {str(e)}")
        else:
            action_msg = "Từ chối đề xuất tài liệu"

        # Xóa yêu cầu sau khi xử lý
        self.requests = [req for req in self.requests if req['request_id'] != request_id]
        self._save_requests()
        self._log_action("approve_request", "", f"{action_msg}: {request['title']}")
        return True

    def get_pending_requests(self) -> List[Dict]:
        """
        Lấy danh sách các yêu cầu đề xuất tài liệu chờ xử lý
        """
        return self.requests

    def get_pending_ratings(self) -> List[Dict]:
        """
        Lấy danh sách các đánh giá chờ duyệt
        """
        return [r for r in self.ratings if not r['approved']]

    def get_recommendations(self, min_rating: float = 4.0, min_reviews: int = 3) -> List[Dict]:
        """
        Lấy danh sách tài liệu được đề xuất dựa trên đánh giá
        """
        recommended = []
        for doc in self.documents:
            avg_rating = self.get_average_rating(doc['doc_id'])
            if avg_rating is None:
                continue
                
            ratings_count = len(self.get_ratings(doc['doc_id'], approved_only=True))
            if avg_rating >= min_rating and ratings_count >= min_reviews:
                doc_copy = doc.copy()
                doc_copy['average_rating'] = avg_rating
                doc_copy['rating_count'] = ratings_count
                recommended.append(doc_copy)
        
        # Sắp xếp theo điểm đánh giá giảm dần
        return sorted(recommended, key=lambda x: x['average_rating'], reverse=True)
    def restore_document(self, doc_id: str) -> bool:
        document = self.get_document_details(doc_id, include_deleted=True)
        if not document:
            raise ValueError("Tài liệu không tồn tại!")
    
        if not document.get('deleted', False):
            raise ValueError("Tài liệu chưa bị xóa, không cần khôi phục!")
    
        document['deleted'] = False
        self._update_status(document)  # Cập nhật trạng thái tài liệu
        self._save_documents()
        self._log_action("restore", doc_id, f"Khôi phục tài liệu: {document['title']}")
        return True
    def get_document_details(self, doc_id: str, include_deleted: bool = False) -> Optional[Dict]:
        doc = next((doc for doc in self.documents if doc['doc_id'] == doc_id), None)
        if not doc:
            self._log_action("get_document_details", doc_id, f"Không tìm thấy tài liệu với doc_id: {doc_id}")
            return None
        if doc.get('deleted', False) and not include_deleted:
            self._log_action("get_document_details", doc_id, f"Tài liệu {doc_id} đã bị xóa, không thể truy cập")
            return None
        return doc