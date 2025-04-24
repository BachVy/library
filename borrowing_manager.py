import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from reader_manager import ReaderManager
from document_manager import DocumentManager

class BorrowingManager:
    def __init__(self, borrow_file: str = "borrow_records.json", 
                 return_file: str = "return_records.json", 
                 log_file: str = "borrowing_logs.json",
                 reservation_file: str = "reservation_records.json"):
        self.borrow_file = borrow_file
        self.return_file = return_file
        self.log_file = log_file
        self.reservation_file = reservation_file
        self.borrow_records = self._load_borrow_records()
        self.return_records = self._load_return_records()
        self.logs = self._load_logs()
        self.reservation_records = self._load_reservation_records()

    def _load_borrow_records(self) -> List[Dict]:
        try:
            with open(self.borrow_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            os.makedirs(os.path.dirname(self.borrow_file), exist_ok=True)
            with open(self.borrow_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=4)
            return []

    def _load_return_records(self) -> List[Dict]:
        try:
            with open(self.return_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            os.makedirs(os.path.dirname(self.return_file), exist_ok=True)
            with open(self.return_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=4)
            return []

    def _load_logs(self) -> List[Dict]:
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=4)
            return []

    def _load_reservation_records(self) -> List[Dict]:
        try:
            with open(self.reservation_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            os.makedirs(os.path.dirname(self.reservation_file), exist_ok=True)
            with open(self.reservation_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=4)
            return []

    def _save_borrow_records(self):
        os.makedirs(os.path.dirname(self.borrow_file), exist_ok=True)
        with open(self.borrow_file, 'w', encoding='utf-8') as f:
            json.dump(self.borrow_records, f, ensure_ascii=False, indent=4)

    def _save_return_records(self):
        os.makedirs(os.path.dirname(self.return_file), exist_ok=True)
        with open(self.return_file, 'w', encoding='utf-8') as f:
            json.dump(self.return_records, f, ensure_ascii=False, indent=4)

    def _save_logs(self):
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(self.logs, f, ensure_ascii=False, indent=4)

    def _save_reservation_records(self):
        os.makedirs(os.path.dirname(self.reservation_file), exist_ok=True)
        with open(self.reservation_file, 'w', encoding='utf-8') as f:
            json.dump(self.reservation_records, f, ensure_ascii=False, indent=4)

    def _log_action(self, action: str, record_id: str, details: str):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "record_id": record_id,
            "details": details
        }
        self.logs.append(log_entry)
        self._save_logs()

    def _generate_borrow_id(self) -> str:
        return f"BR{str(len(self.borrow_records) + 1).zfill(5)}"

    def _generate_return_id(self) -> str:
        return f"RT{str(len(self.return_records) + 1).zfill(5)}"

    def _generate_reservation_id(self) -> str:
        return f"RS{str(len(self.reservation_records) + 1).zfill(5)}"

    def create_borrow_record(self, reader_id: str, doc_ids: List[str], 
                            reader_manager: ReaderManager, 
                            doc_manager: DocumentManager) -> Dict:
        reader = reader_manager.get_reader_details(reader_id)
        if not reader:
            raise ValueError("Không tìm thấy độc giả")

        if reader['status'] != 'active':
            raise ValueError("Tài khoản không ở trạng thái hoạt động")

        expiry_date = datetime.fromisoformat(reader['expiry_date'])
        if expiry_date < datetime.now():
            raise ValueError("Tài khoản đã hết hạn")

        if not reader['annual_fee_paid']:
            raise ValueError("Phí thường niên chưa được thanh toán")

        max_books = reader.get('max_books', 5)
        if reader['borrowed_books'] + len(doc_ids) > max_books:
            raise ValueError(f"Số lượng tài liệu mượn vượt quá giới hạn ({max_books})")

        documents = []
        for doc_id in doc_ids:
            doc = doc_manager.get_document_details(doc_id)
            if not doc:
                raise ValueError(f"Không tìm thấy tài liệu {doc_id}")
            if doc['status'] != 'available':
                raise ValueError(f"Tài liệu {doc_id} hiện không có sẵn để mượn")
            if doc['DacBiet'] and not reader['special_document']:
                raise ValueError(f"Độc giả không có quyền truy cập tài liệu đặc biệt {doc_id}")
            documents.append(doc)

        borrow_id = self._generate_borrow_id()
        borrow_date = datetime.now().isoformat()
        due_date = (datetime.now() + timedelta(days=reader['max_days'])).isoformat()

        for doc_id in doc_ids:
            reader_manager.add_borrow_record(reader_id, doc_id, borrow_date, due_date)
            doc_manager.borrow_document(doc_id)

        borrow_record = {
            "borrow_id": borrow_id,
            "reader_id": reader_id,
            "borrow_date": borrow_date,
            "due_date": due_date,
            "documents": doc_ids,
            "quantity": len(doc_ids),
            "status": "borrowed"
        }
        self.borrow_records.append(borrow_record)
        self._save_borrow_records()
        self._log_action("create_borrow", borrow_id, f"Lập phiếu mượn cho độc giả {reader_id}")
        return borrow_record

    def search_borrow_records(self, borrow_id: Optional[str] = None, 
                             reader_id: Optional[str] = None) -> List[Dict]:
        results = []
        for record in self.borrow_records:
            match = True
            if borrow_id and borrow_id.lower() not in record['borrow_id'].lower():
                match = False
            if reader_id and reader_id.lower() not in record['reader_id'].lower():
                match = False
            if match:
                results.append({
                    "stt": len(results) + 1,
                    "borrow_id": record['borrow_id'],
                    "reader_id": record['reader_id'],
                    "borrow_date": record['borrow_date'],
                    "due_date": record['due_date'],
                    "quantity": record['quantity'],
                    "status": record['status']
                })
        return results

    def get_overdue_borrow_records(self) -> List[Dict]:
        overdue_records = []
        for record in self.borrow_records:
            if record['status'] == 'borrowed':
                due_date = datetime.fromisoformat(record['due_date'])
                if due_date < datetime.now():
                    overdue_records.append({
                        "stt": len(overdue_records) + 1,
                        "borrow_id": record['borrow_id'],
                        "reader_id": record['reader_id'],
                        "borrow_date": record['borrow_date'],
                        "due_date": record['due_date'],
                        "quantity": record['quantity'],
                        "status": record['status']
                    })
        return overdue_records

    def get_unreturned_borrow_records(self) -> List[Dict]:
        return [{
            "stt": idx + 1,
            "borrow_id": record['borrow_id'],
            "reader_id": record['reader_id'],
            "borrow_date": record['borrow_date'],
            "due_date": record['due_date'],
            "quantity": record['quantity'],
            "status": record['status']
        } for idx, record in enumerate(self.borrow_records) if record['status'] == 'borrowed']

    def get_borrow_record_details(self, borrow_id: str) -> Optional[Dict]:
        return next((record for record in self.borrow_records if record['borrow_id'] == borrow_id), None)

    def update_borrow_record(self, borrow_id: str, new_doc_ids: List[str], 
                            reader_manager: ReaderManager, 
                            doc_manager: DocumentManager) -> bool:
        record = self.get_borrow_record_details(borrow_id)
        if not record:
            return False

        if record['status'] != 'borrowed':
            raise ValueError("Không thể cập nhật phiếu mượn đã hoàn tất")

        reader = reader_manager.get_reader_details(record['reader_id'])
        if not reader:
            raise ValueError("Không tìm thấy độc giả")

        max_books = reader.get('max_books', 5)
        current_borrowed = reader['borrowed_books'] - record['quantity'] + len(new_doc_ids)
        if current_borrowed > max_books:
            raise ValueError(f"Số lượng tài liệu mượn vượt quá giới hạn ({max_books})")

        old_doc_ids = record['documents']
        for doc_id in old_doc_ids:
            for borrow_record in reader['borrow_history']:
                if borrow_record['book_id'] == doc_id and borrow_record['status'] == 'borrowed':
                    borrow_record['status'] = 'cancelled'
                    reader['borrowed_books'] -= 1
                    break
            doc_manager.return_document(doc_id)

        documents = []
        for doc_id in new_doc_ids:
            doc = doc_manager.get_document_details(doc_id)
            if not doc:
                raise ValueError(f"Không tìm thấy tài liệu {doc_id}")
            if doc['status'] != 'available':
                raise ValueError(f"Tài liệu {doc_id} hiện không có sẵn để mượn")
            if doc['DacBiet'] and not reader['special_document']:
                raise ValueError(f"Độc giả không có quyền truy cập tài liệu đặc biệt {doc_id}")
            documents.append(doc)

        for doc_id in new_doc_ids:
            reader_manager.add_borrow_record(record['reader_id'], doc_id, 
                                            record['borrow_date'], record['due_date'])
            doc_manager.borrow_document(doc_id)

        record['documents'] = new_doc_ids
        record['quantity'] = len(new_doc_ids)
        reader_manager._save_readers()
        self._save_borrow_records()
        self._log_action("update_borrow", borrow_id, f"Cập nhật phiếu mượn cho độc giả {record['reader_id']}")
        return True

    def delete_borrow_record(self, borrow_id: str, 
                            reader_manager: ReaderManager, 
                            doc_manager: DocumentManager) -> bool:
        record = self.get_borrow_record_details(borrow_id)
        if not record:
            return False

        if record['status'] != 'borrowed':
            raise ValueError("Không thể xóa phiếu mượn đã hoàn tất")

        reader = reader_manager.get_reader_details(record['reader_id'])
        if not reader:
            raise ValueError("Không tìm thấy độc giả")

        for doc_id in record['documents']:
            for borrow_record in reader['borrow_history']:
                if borrow_record['book_id'] == doc_id and borrow_record['status'] == 'borrowed':
                    borrow_record['status'] = 'cancelled'
                    reader['borrowed_books'] -= 1
                    break
            doc_manager.return_document(doc_id)

        self.borrow_records = [r for r in self.borrow_records if r['borrow_id'] != borrow_id]
        reader_manager._save_readers()
        doc_manager._save_documents()
        self._save_borrow_records()
        self._log_action("delete_borrow", borrow_id, f"Xóa phiếu mượn cho độc giả {record['reader_id']}")
        return True

    def create_return_record(self, borrow_id: str, doc_ids: List[str], 
                            reader_manager: ReaderManager, 
                            doc_manager: DocumentManager) -> Dict:
        borrow_record = self.get_borrow_record_details(borrow_id)
        if not borrow_record:
            raise ValueError("Không tìm thấy phiếu mượn")

        if borrow_record['status'] != 'borrowed':
            raise ValueError("Phiếu mượn đã hoàn tất, không thể lập phiếu trả")

        reader = reader_manager.get_reader_details(borrow_record['reader_id'])
        if not reader:
            raise ValueError("Không tìm thấy độc giả")

        invalid_docs = [doc_id for doc_id in doc_ids if doc_id not in borrow_record['documents']]
        if invalid_docs:
            raise ValueError(f"Các tài liệu {invalid_docs} không thuộc phiếu mượn này")

        return_id = self._generate_return_id()
        return_date = datetime.now().isoformat()
        total_fine = 0

        for doc_id in doc_ids:
            result = reader_manager.return_book(borrow_record['reader_id'], doc_id, return_date)
            if result['success']:
                doc_manager.return_document(doc_id)
                total_fine += result['fine']

        remaining_docs = [doc_id for doc_id in borrow_record['documents'] if doc_id not in doc_ids]
        if not remaining_docs:
            borrow_record['status'] = 'returned'

        return_record = {
            "return_id": return_id,
            "borrow_id": borrow_id,
            "reader_id": borrow_record['reader_id'],
            "return_date": return_date,
            "documents": doc_ids,
            "total_fine": total_fine
        }
        self.return_records.append(return_record)
        reader_manager._save_readers()
        doc_manager._save_documents()
        self._save_borrow_records()
        self._save_return_records()
        self._log_action("create_return", return_id, f"Lập phiếu trả cho phiếu mượn {borrow_id}, Phí phạt: {total_fine} VNĐ")
        return return_record

    def search_return_records(self, return_id: Optional[str] = None, 
                             borrow_id: Optional[str] = None, 
                             reader_id: Optional[str] = None) -> List[Dict]:
        results = []
        for record in self.return_records:
            match = True
            if return_id and return_id.lower() not in record['return_id'].lower():
                match = False
            if borrow_id and borrow_id.lower() not in record['borrow_id'].lower():
                match = False
            if reader_id and reader_id.lower() not in record['reader_id'].lower():
                match = False
            if match:
                results.append({
                    "stt": len(results) + 1,
                    "return_id": record['return_id'],
                    "borrow_id": record['borrow_id'],
                    "reader_id": record['reader_id'],
                    "return_date": record['return_date'],
                    "total_fine": record['total_fine']
                })
        return results

    def get_all_return_records(self) -> List[Dict]:
        return [{
            "stt": idx + 1,
            "return_id": record['return_id'],
            "borrow_id": record['borrow_id'],
            "reader_id": record['reader_id'],
            "return_date": record['return_date'],
            "total_fine": record['total_fine']
        } for idx, record in enumerate(self.return_records)]

    def get_return_record_details(self, return_id: str) -> Optional[Dict]:
        return next((record for record in self.return_records if record['return_id'] == return_id), None)

    def update_return_record(self, return_id: str, new_doc_ids: List[str], 
                            reader_manager: ReaderManager, 
                            doc_manager: DocumentManager) -> bool:
        return_record = self.get_return_record_details(return_id)
        if not return_record:
            return False

        borrow_record = self.get_borrow_record_details(return_record['borrow_id'])
        if not borrow_record:
            raise ValueError("Không tìm thấy phiếu mượn liên quan")

        reader = reader_manager.get_reader_details(return_record['reader_id'])
        if not reader:
            raise ValueError("Không tìm thấy độc giả")

        old_doc_ids = return_record['documents']
        for doc_id in old_doc_ids:
            for history in reader['borrow_history']:
                if history['book_id'] == doc_id and history['status'] == 'returned':
                    history['status'] = 'borrowed'
                    reader['borrowed_books'] += 1
                    reader['fine_amount'] -= history['fine']
                    break
            doc_manager.borrow_document(doc_id)

        invalid_docs = [doc_id for doc_id in new_doc_ids if doc_id not in borrow_record['documents']]
        if invalid_docs:
            raise ValueError(f"Các tài liệu {invalid_docs} không thuộc phiếu mượn này")

        total_fine = 0
        for doc_id in new_doc_ids:
            result = reader_manager.return_book(return_record['reader_id'], doc_id, return_record['return_date'])
            if result['success']:
                doc_manager.return_document(doc_id)
                total_fine += result['fine']

        remaining_docs = [doc_id for doc_id in borrow_record['documents'] if doc_id not in new_doc_ids]
        if not remaining_docs:
            borrow_record['status'] = 'returned'
        else:
            borrow_record['status'] = 'borrowed'

        return_record['documents'] = new_doc_ids
        return_record['total_fine'] = total_fine
        reader_manager._save_readers()
        doc_manager._save_documents()
        self._save_borrow_records()
        self._save_return_records()
        self._log_action("update_return", return_id, f"Cập nhật phiếu trả cho phiếu mượn {return_record['borrow_id']}")
        return True

    def delete_return_record(self, return_id: str, 
                            reader_manager: ReaderManager, 
                            doc_manager: DocumentManager) -> bool:
        return_record = self.get_return_record_details(return_id)
        if not return_record:
            return False

        borrow_record = self.get_borrow_record_details(return_record['borrow_id'])
        if not borrow_record:
            raise ValueError("Không tìm thấy phiếu mượn liên quan")

        reader = reader_manager.get_reader_details(return_record['reader_id'])
        if not reader:
            raise ValueError("Không tìm thấy độc giả")

        for doc_id in return_record['documents']:
            for history in reader['borrow_history']:
                if history['book_id'] == doc_id and history['status'] == 'returned':
                    history['status'] = 'borrowed'
                    reader['borrowed_books'] += 1
                    reader['fine_amount'] -= history['fine']
                    break
            doc_manager.borrow_document(doc_id)

        borrow_record['status'] = 'borrowed'
        self.return_records = [r for r in self.return_records if r['return_id'] != return_id]
        reader_manager._save_readers()
        doc_manager._save_documents()
        self._save_borrow_records()
        self._save_return_records()
        self._log_action("delete_return", return_id, f"Xóa phiếu trả cho phiếu mượn {return_record['borrow_id']}")
        return True

    def extend_borrow_period(self, borrow_id: str, reader_manager: ReaderManager) -> bool:
        borrow_record = self.get_borrow_record_details(borrow_id)
        if not borrow_record:
            raise ValueError("Không tìm thấy phiếu mượn")

        if borrow_record['status'] != 'borrowed':
            raise ValueError("Chỉ có thể gia hạn phiếu mượn đang hoạt động")

        for doc_id in borrow_record['documents']:
            if any(res['doc_id'] == doc_id and res['status'] == 'pending' 
                  for res in self.reservation_records):
                raise ValueError(f"Không thể gia hạn vì tài liệu {doc_id} có người đặt trước")

        reader = reader_manager.get_reader_details(borrow_record['reader_id'])
        if not reader:
            raise ValueError("Không tìm thấy độc giả")

        for history in reader['borrow_history']:
            if history['book_id'] in borrow_record['documents'] and history.get('extended', False):
                raise ValueError("Đã gia hạn mượn tài liệu này trước đó")

        new_due_date = (datetime.fromisoformat(borrow_record['due_date']) + timedelta(days=7)).isoformat()
        borrow_record['due_date'] = new_due_date

        for doc_id in borrow_record['documents']:
            for history in reader['borrow_history']:
                if history['book_id'] == doc_id and history['status'] == 'borrowed':
                    history['due_date'] = new_due_date
                    history['extended'] = True
                    break

        self._save_borrow_records()
        reader_manager._save_readers()
        self._log_action("extend_borrow", borrow_id, f"Gia hạn mượn đến {new_due_date}")
        return True

    def create_reservation(self, reader_id: str, doc_id: str, 
                          reader_manager: ReaderManager, 
                          doc_manager: DocumentManager) -> Dict:
        reader = reader_manager.get_reader_details(reader_id)
        if not reader:
            raise ValueError("Không tìm thấy độc giả")

        current_reservations = sum(1 for res in self.reservation_records 
                                 if res['reader_id'] == reader_id and res['status'] == 'pending')
        if current_reservations >= 2:
            raise ValueError("Mỗi độc giả chỉ được đặt trước tối đa 2 tài liệu")

        document = doc_manager.get_document_details(doc_id)
        if not document:
            raise ValueError("Không tìm thấy tài liệu")

        if document['status'] == 'available':
            raise ValueError("Không thể đặt trước tài liệu đang có sẵn")

        if any(hist['book_id'] == doc_id and hist['status'] == 'borrowed' 
              for hist in reader['borrow_history']):
            raise ValueError("Bạn đang mượn tài liệu này, không thể đặt trước")

        if any(res['doc_id'] == doc_id and res['status'] == 'pending' 
              for res in self.reservation_records):
            raise ValueError("Tài liệu này đã có người đặt trước")

        reservation = {
            "reservation_id": self._generate_reservation_id(),
            "reader_id": reader_id,
            "doc_id": doc_id,
            "reservation_date": datetime.now().isoformat(),
            "expiry_date": (datetime.now() + timedelta(days=14)).isoformat(),
            "status": "pending",
            "notified": False
        }

        self.reservation_records.append(reservation)
        self._save_reservation_records()
        self._log_action("create_reservation", reservation['reservation_id'], 
                         f"Đặt trước tài liệu {doc_id} bởi độc giả {reader_id}")
        return reservation

    def cancel_reservation(self, reservation_id: str) -> bool:
        reservation = next((res for res in self.reservation_records 
                          if res['reservation_id'] == reservation_id), None)
        if not reservation:
            return False

        if reservation['status'] != 'pending':
            raise ValueError("Chỉ có thể hủy đặt trước đang chờ")

        reservation['status'] = 'cancelled'
        self._save_reservation_records()
        self._log_action("cancel_reservation", reservation_id, 
                        f"Hủy đặt trước tài liệu {reservation['doc_id']}")
        return True

    def check_reservation_availability(self, doc_id: str) -> bool:
        document = next((doc for doc in self.documents if doc['doc_id'] == doc_id), None)
        if not document:
            return False

        if document['status'] != 'available':
            return False

        pending_reservations = [res for res in self.reservation_records 
                              if res['doc_id'] == doc_id and res['status'] == 'pending']
        if not pending_reservations:
            return False

        pending_reservations.sort(key=lambda x: x['reservation_date'])

        first_reservation = pending_reservations[0]
        first_reservation['status'] = 'ready'
        first_reservation['expiry_date'] = (datetime.now() + timedelta(days=3)).isoformat()
        self._save_reservation_records()
        return True

    def get_pending_reservations(self, reader_id: Optional[str] = None) -> List[Dict]:
        results = [res for res in self.reservation_records if res['status'] == 'pending']
        if reader_id:
            results = [res for res in results if res['reader_id'] == reader_id]
        return results

    def get_ready_reservations(self, reader_id: Optional[str] = None) -> List[Dict]:
        results = [res for res in self.reservation_records if res['status'] == 'ready']
        if reader_id:
            results = [res for res in results if res['reader_id'] == reader_id]
        return results

    def complete_reservation(self, reservation_id: str, 
                            reader_manager: ReaderManager, 
                            doc_manager: DocumentManager) -> bool:
        reservation = next((res for res in self.reservation_records 
                          if res['reservation_id'] == reservation_id), None)
        if not reservation:
            return False

        if reservation['status'] != 'ready':
            raise ValueError("Chỉ có thể hoàn tất đặt trước đã sẵn sàng")

        document = doc_manager.get_document_details(reservation['doc_id'])
        if not document or document['status'] != 'available':
            raise ValueError("Tài liệu không có sẵn để mượn")

        self.create_borrow_record(
            reader_id=reservation['reader_id'],
            doc_ids=[reservation['doc_id']],
            reader_manager=reader_manager,
            doc_manager=doc_manager
        )

        reservation['status'] = 'completed'
        self._save_reservation_records()
        self._log_action("complete_reservation", reservation_id, 
                        f"Hoàn tất đặt trước, tài liệu {reservation['doc_id']} đã được mượn")
        return True

    def notify_ready_reservations(self):
        ready_reservations = [res for res in self.reservation_records 
                            if res['status'] == 'ready' and not res['notified']]
        
        for res in ready_reservations:
            res['notified'] = True
            self._log_action("notify_reservation", res['reservation_id'], 
                            f"Đã thông báo tài liệu {res['doc_id']} sẵn sàng cho độc giả {res['reader_id']}")

        if ready_reservations:
            self._save_reservation_records()