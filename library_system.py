from datetime import datetime, timedelta
from typing import List, Dict, Optional
from reader_manager import ReaderManager
from document_manager import DocumentManager
from borrowing_manager import BorrowingManager

if __name__ == "__main__":
    reader_manager = ReaderManager(
        readers_file=r"E:\Python\library\users.json",
        reader_types_file=r"E:\Python\library\reader_types.json",
        log_file=r"E:\Python\library\reader_logs.json"
    )
    doc_manager = DocumentManager(r"E:\Python\library\documents.json")
    borrowing_manager = BorrowingManager()

    def get_non_empty_input(prompt: str) -> str:
        while True:
            value = input(prompt).strip()
            if value:
                return value
            print("Giá trị không được để trống. Vui lòng nhập lại.")

    def get_optional_input(prompt: str) -> Optional[str]:
        value = input(prompt).strip()
        return value if value else None

    def get_yes_no_input(prompt: str) -> str:
        while True:
            value = input(prompt).strip().lower()
            if value in ['y', 'n']:
                return value
            print("Vui lòng nhập Y hoặc N.")

    while True:
        print("\n=== HỆ THỐNG QUẢN LÝ THƯ VIỆN ===")
        print("1. Quản lý độc giả")
        print("2. Quản lý tài liệu")
        print("3. Quản lý phiếu mượn")
        print("4. Quản lý phiếu trả")
        print("5. Thống kê")
        print("6. Thoát")
        choice = input("Chọn chức năng (1-6): ").strip()

        if choice == "1":  # Quản lý độc giả
            while True:
                print("\n=== QUẢN LÝ ĐỘC GIẢ ===")
                print("1. Đăng ký độc giả mới")
                print("2. Tìm kiếm độc giả")
                print("3. Gia hạn tài khoản")
                print("4. Tạm khóa độc giả")
                print("5. Xóa độc giả")
                print("6. Cập nhật thông tin độc giả")
                print("7. Khôi phục tài khoản")
                print("8. Xem danh sách độc giả có phí phạt")
                print("9. Quay lại")
                sub_choice = input("Chọn chức năng (1-9): ").strip()

                if sub_choice == "1":  # Đăng ký độc giả mới
                    try:
                        full_name = get_non_empty_input("Nhập họ tên: ")
                        id_card = get_non_empty_input("Nhập CMND/CCCD: ")
                        dob = get_optional_input("Nhập ngày sinh (YYYY-MM-DD, nhấn Enter nếu không có): ")
                        phone = get_non_empty_input("Nhập số điện thoại: ")
                        email = get_non_empty_input("Nhập email: ")
                        address = get_non_empty_input("Nhập địa chỉ: ")
                        print("Các loại độc giả:", [rt['type'] for rt in reader_manager.reader_types])
                        reader_type = get_non_empty_input("Nhập loại độc giả (Sinh viên, Giảng viên/Cán bộ, Khách vãng lai): ")
                
                        student_id = None
                        employee_id = None
                        if reader_type == "Sinh viên":
                            student_id = get_non_empty_input("Nhập mã số sinh viên (6-10 ký tự chữ in hoa hoặc số): ")
                        elif reader_type == "Giảng viên/Cán bộ":
                            employee_id = get_non_empty_input("Nhập mã số cán bộ (bắt đầu bằng 'CB', 6-10 ký tự chữ in hoa hoặc số): ")

                        new_reader = reader_manager.register_reader(
                            full_name=full_name,
                            id_card=id_card,
                            dob=dob,
                            phone=phone,
                            email=email,
                            address=address,
                            reader_type=reader_type,
                            student_id=student_id,
                            employee_id=employee_id
                        )
                        print(f"Đăng ký thành công! Mã độc giả: {new_reader['reader_id']}, Mật khẩu: {new_reader['password']}")
                    except ValueError as e:
                        print(f"Lỗi đăng ký: {e}")

                elif sub_choice == "2":  # Tìm kiếm độc giả
                    reader_id = get_optional_input("Nhập mã độc giả (nhấn Enter nếu không tìm theo mã): ")
                    id_number = get_optional_input("Nhập CMND/MSSV/MSCB (nhấn Enter nếu không tìm theo số định danh): ")
                    full_name = get_optional_input("Nhập họ tên (nhấn Enter nếu không tìm theo tên): ")
                    email = get_optional_input("Nhập email (nhấn Enter nếu không tìm theo email): ")
                    results = reader_manager.search_readers(reader_id=reader_id, id_number=id_number, full_name=full_name, email=email)
                    if results:
                        print("\nKết quả tìm kiếm:")
                        for result in results:
                            print(result)
                    else:
                        print("Không tìm thấy độc giả phù hợp.")

                elif sub_choice == "3":  # Gia hạn tài khoản
                    try:
                        reader_id = get_non_empty_input("Nhập mã độc giả: ")
                        reader_manager.renew_account(reader_id)
                        print("Gia hạn tài khoản thành công!")
                    except ValueError as e:
                        print(f"Lỗi gia hạn: {e}")

                elif sub_choice == "4":  # Tạm khóa độc giả
                    try:
                        reader_id = get_non_empty_input("Nhập mã độc giả: ")
                        reason = get_non_empty_input("Nhập lý do tạm khóa: ")
                        reader_manager.suspend_reader(reader_id, reason)
                        print("Tạm khóa độc giả thành công!")
                    except ValueError as e:
                        print(f"Lỗi tạm khóa: {e}")

                elif sub_choice == "5":  # Xóa độc giả
                    try:
                        reader_id = get_non_empty_input("Nhập mã độc giả: ")
                        reader_manager.delete_reader(reader_id)
                        print("Xóa độc giả thành công!")
                    except ValueError as e:
                        print(f"Lỗi xóa độc giả: {e}")

                elif sub_choice == "6":  # Cập nhật thông tin độc giả
                    try:
                        reader_id = get_non_empty_input("Nhập mã độc giả: ")
                        full_name = get_optional_input("Nhập họ tên mới (nhấn Enter nếu không thay đổi): ")
                        phone = get_optional_input("Nhập số điện thoại mới (nhấn Enter nếu không thay đổi): ")
                        email = get_optional_input("Nhập email mới (nhấn Enter nếu không thay đổi): ")
                        address = get_optional_input("Nhập địa chỉ mới (nhấn Enter nếu không thay đổi): ")

                        if not any([full_name, phone, email, address]):
                            print("Vui lòng cung cấp ít nhất một thông tin để cập nhật.")
                            continue

                        reader_manager.update_reader_info(
                            reader_id=reader_id,
                            full_name=full_name,
                            phone=phone,
                            email=email,
                            address=address
                        )
                        print("Cập nhật thông tin độc giả thành công!")
                    except ValueError as e:
                        print(f"Lỗi cập nhật: {e}")

                elif sub_choice == "7":  # Khôi phục tài khoản
                    try:
                        reader_id = get_non_empty_input("Nhập mã độc giả: ")

                        # Kiểm tra độc giả tồn tại
                        reader = reader_manager.get_reader_details(reader_id)
                        if not reader:
                            print("Độc giả không tồn tại!")
                            continue

                        # Hiển thị thông tin độc giả
                        print("\nThông tin độc giả:")
                        print(f"Mã độc giả: {reader['reader_id']}")
                        print(f"Họ tên: {reader['full_name']}")
                        print(f"Trạng thái: {reader['status']}")
                        print(f"Phí phạt chưa thanh toán: {reader.get('fine_amount', 0)} VNĐ")
                        print(f"Phí thường niên: {'Đã thanh toán' if reader['annual_fee_paid'] else 'Chưa thanh toán'}")
                        print(f"Ngày hết hạn: {reader['expiry_date']}")

                        # Kiểm tra trạng thái trước
                        if reader['status'] not in ['suspended', 'expired']:
                            print("Tài khoản không cần khôi phục (đã ở trạng thái active)!")
                            continue

                        # Xác nhận trước khi khôi phục
                        confirm = get_yes_no_input("Bạn có chắc chắn muốn khôi phục tài khoản này (Y/N)? ")
                        if confirm.lower() != 'y':
                            print("Hủy thao tác khôi phục.")
                            continue

                        # Nhập thông tin thanh toán
                        paid_fine = get_yes_no_input("Đã thanh toán phí phạt (Y/N)? ") if reader.get('fine_amount', 0) > 0 else 'y'
                        paid_annual_fee = get_yes_no_input("Đã thanh toán phí thường niên (Y/N)? ") if not reader['annual_fee_paid'] else 'y'

                        # Gọi restore_account
                        reader_manager.restore_account(
                            reader_id=reader_id,
                            paid_fine=paid_fine.lower() == 'y',
                            paid_annual_fee=paid_annual_fee.lower() == 'y'
                        )

                        # Hiển thị trạng thái sau khi khôi phục
                        reader = reader_manager.get_reader_details(reader_id)
                        print("\nKhôi phục tài khoản thành công!")
                        print(f"Trạng thái mới: {reader['status']}")
                        print(f"Phí phạt: {reader.get('fine_amount', 0)} VNĐ")
                        print(f"Phí thường niên: {'Đã thanh toán' if reader['annual_fee_paid'] else 'Chưa thanh toán'}")
                        print(f"Ngày hết hạn mới: {reader['expiry_date']}")
                    except ValueError as e:
                        print(f"Lỗi khôi phục tài khoản: {e}")
                elif sub_choice == "8":  # Xem danh sách độc giả có phí phạt
                    readers_with_fines = reader_manager.get_readers_with_fines()
                    if not readers_with_fines:
                        print("Không có độc giả nào có phí phạt!")
                    else:
                        print("\nDanh sách độc giả có phí phạt:")
                        print("---------------------------------------------")
                        for reader in readers_with_fines:
                            reader_details = reader_manager.get_reader_details(reader['reader_id'])
                            annual_fee_status = 'Đã thanh toán' if reader_details['annual_fee_paid'] else 'Chưa thanh toán'
                            print(f"Mã độc giả: {reader['reader_id']}")
                            print(f"Họ tên: {reader['full_name']}")
                            print(f"Phí phạt: {reader['fine_amount']} VNĐ")
                          #  print(f"Trạng thái: {reader['status']}")
                            print(f"Phí thường niên: {annual_fee_status}")
                            print("---------------------------------------------")

                        # Thêm tùy chọn khôi phục tài khoản ngay
                        restore_now = get_yes_no_input("\nBạn có muốn khôi phục tài khoản cho một độc giả trong danh sách (Y/N)? ")
                        if restore_now.lower() == 'y':
                            try:
                                reader_id = get_non_empty_input("Nhập mã độc giả cần khôi phục: ")
                                reader = reader_manager.get_reader_details(reader_id)
                                if not reader:
                                    print("Độc giả không tồn tại!")
                                    continue

                                print("\nThông tin độc giả:")
                                print("---------------------------------------------")
                                print(f"Mã độc giả: {reader['reader_id']}")
                                print(f"Họ tên: {reader['full_name']}")
                                print(f"Trạng thái: {reader['status']}")
                                print(f"Phí phạt: {reader.get('fine_amount', 0)} VNĐ")
                                print(f"Phí thường niên: {'Đã thanh toán' if reader['annual_fee_paid'] else 'Chưa thanh toán'}")
                                print(f"Ngày hết hạn: {reader['expiry_date']}")
                                print("---------------------------------------------")

                                if reader['status'] not in ['suspended', 'expired']:
                                    print("Tài khoản không cần khôi phục (đã ở trạng thái active)!")
                                    continue

                                confirm = get_yes_no_input("Bạn có chắc chắn muốn khôi phục tài khoản này (Y/N)? ")
                                if confirm.lower() != 'y':
                                    print("Hủy thao tác khôi phục.")
                                    continue

                                paid_fine = get_yes_no_input("Đã thanh toán phí phạt (Y/N)? ") if reader.get('fine_amount', 0) > 0 else 'y'
                                paid_annual_fee = get_yes_no_input("Đã thanh toán phí thường niên (Y/N)? ") if not reader['annual_fee_paid'] else 'y'

                                reader_manager.restore_account(
                                    reader_id=reader_id,
                                    paid_fine=paid_fine.lower() == 'y',
                                    paid_annual_fee=paid_annual_fee.lower() == 'y'
                                )

                                reader = reader_manager.get_reader_details(reader_id)
                                print("\nKhôi phục tài khoản thành công!")
                                print("---------------------------------------------")
                                print(f"Trạng thái mới: {reader['status']}")
                                print(f"Phí phạt: {reader.get('fine_amount', 0)} VNĐ")
                                print(f"Phí thường niên: {'Đã thanh toán' if reader['annual_fee_paid'] else 'Chưa thanh toán'}")
                                print(f"Ngày hết hạn mới: {reader['expiry_date']}")
                                print("---------------------------------------------")

                                if reader['notifications']:
                                    print("Thông báo đã gửi:")
                                    for notif in reader['notifications'][-1:]:
                                        print(f"- {notif['timestamp']}: {notif['message']}")

                            except ValueError as e:
                                print(f"Lỗi khôi phục tài khoản: {e}")

                elif sub_choice == "9":  # Quay lại
                    break
        elif choice == "2":  # Quản lý tài liệu
            while True:
                print("\n=== QUẢN LÝ TÀI LIỆU ===")
                print("1. Thêm tài liệu mới")
                print("2. Tìm kiếm tài liệu")
                print("3. Xem toàn bộ danh sách tài liệu")
                print("4. Xem/Chỉnh sửa thông tin tài liệu")
                print("5. Xóa tài liệu")
                print("6. Cập nhật thông tin tài liệu")
                print("7. Khôi phục tài liệu")
                print("8. Quay lại")
                sub_choice = input("Chọn chức năng (1-8): ").strip()

                if sub_choice == "1": 
                    try:
                        title = get_non_empty_input("Nhập tiêu đề tài liệu: ")
                        category = get_non_empty_input("Nhập lĩnh vực (SÁCH, TẠP CHÍ, CÔNG TRÌNH NGHIÊN CỨU, ...): ")
                        SoLuong = int(get_non_empty_input("Nhập tổng số lượng: "))
                        DacBiet = get_non_empty_input("Tài liệu có đặc biệt không? (y/n): ").lower() == 'y'
                        new_doc = doc_manager.add_document(title, category, SoLuong, DacBiet)
                        print(f"Thêm tài liệu thành công! Mã tài liệu: {new_doc['doc_id']}")
                    except ValueError as e:
                        print(f"Lỗi thêm tài liệu: {e}")

                elif sub_choice == "2":  
                    doc_id = get_optional_input("Nhập mã tài liệu (nhấn Enter nếu không tìm theo mã): ")
                    title = get_optional_input("Nhập tiêu đề (nhấn Enter nếu không tìm theo tiêu đề): ")
                    category = get_optional_input("Nhập lĩnh vực (nhấn Enter nếu không tìm theo lĩnh vực): ")
                    results = doc_manager.search_documents(doc_id=doc_id, title=title, category=category)
                    if results:
                        print("\nKết quả tìm kiếm:")
                        for result in results:
                            print(result)
                        while True:
                            print("\n=== TÙY CHỌN KẾT QUẢ TÌM KIẾM ===")
                            print("1. Xem chi tiết thông tin tài liệu")
                            print("2. Yêu cầu tài liệu mới")
                            print("3. Quay lại")
                            action_choice = input("Chọn hành động (1-3): ").strip()

                            if action_choice == "1": 
                                doc_id = get_non_empty_input("Nhập mã tài liệu để xem chi tiết: ")
                                doc = doc_manager.get_document_details(doc_id)
                                if doc:
                                    print("\nChi tiết tài liệu:")
                                    print(doc)
                                else:
                                    print("Không tìm thấy tài liệu.")

                            elif action_choice == "2": 
                                try:
                                    title = get_non_empty_input("Nhập tiêu đề tài liệu cần yêu cầu: ")
                                    category = get_non_empty_input("Nhập lĩnh vực: ")
                                    reader_id = get_non_empty_input("Nhập mã độc giả: ")
                                    request = doc_manager.request_document(title, category, reader_id)
                                    print(f"Yêu cầu tài liệu mới thành công! Mã yêu cầu: {request['request_id']}")
                                except ValueError as e:
                                    print(f"Lỗi yêu cầu tài liệu: {e}")

                            elif action_choice == "3":  
                                break

                            else:
                                print("Lựa chọn không hợp lệ. Vui lòng chọn lại.")
                    else:
                        print("Không tìm thấy tài liệu phù hợp.")

                elif sub_choice == "3":  
                    results = doc_manager.search_documents()
                    if results:
                        print("\nDanh sách tài liệu:")
                        for result in results:
                            print(result)
                    else:
                        print("Không có tài liệu nào.")

                elif sub_choice == "4": 
                    doc_id = get_non_empty_input("Nhập mã tài liệu: ")
                    doc = doc_manager.get_document_details(doc_id)
                    if not doc:
                        print("Không tìm thấy tài liệu.")
                        continue

                    print("\nChi tiết tài liệu:")
                    print(doc)
                    edit_choice = input("Bạn có muốn chỉnh sửa thông tin tài liệu không? (y/n): ").strip().lower()
                    if edit_choice == 'y':
                        updates = {}
                        print("Nhập thông tin mới (nhấn Enter để giữ nguyên giá trị hiện tại):")
                        title = get_optional_input(f"Tiêu đề ({doc['title']}): ")
                        if title:
                            updates['title'] = title
                        category = get_optional_input(f"Lĩnh vực ({doc['category']}): ")
                        if category:
                            updates['category'] = category
                        SoLuong = get_optional_input(f"Tổng số lượng ({doc['SoLuong']}): ")
                        if SoLuong:
                            updates['SoLuong'] = int(SoLuong)
                        AvailableQuantity = get_optional_input(f"Số lượng có sẵn ({doc['AvailableQuantity']}): ")
                        if AvailableQuantity:
                            updates['AvailableQuantity'] = int(AvailableQuantity)
                        DacBiet = get_optional_input(f"Đặc biệt (y/n, hiện tại: {doc['DacBiet']}): ")
                        if DacBiet:
                            updates['DacBiet'] = DacBiet.lower() == 'y'

                        if updates:
                            try:
                                doc_manager.update_document(doc_id, updates)
                                print("Cập nhật thông tin tài liệu thành công!")
                            except ValueError as e:
                                print(f"Lỗi cập nhật: {e}")
                        else:
                            print("Không có thay đổi nào được thực hiện.")

                elif sub_choice == "5":  # Xóa tài liệu
                    try:
                        doc_id = get_non_empty_input("Nhập mã tài liệu: ")
                        doc_manager.delete_document(doc_id)
                        print("Xóa tài liệu thành công!")
                    except ValueError as e:
                        print(f"Lỗi xóa tài liệu: {e}")

                elif sub_choice == "6":  # Cập nhật thông tin tài liệu
                    try:
                        doc_id = get_non_empty_input("Nhập mã tài liệu: ")

                        # Kiểm tra tài liệu tồn tại
                        document = doc_manager.get_document_details(doc_id)
                        if not document:
                            print("Tài liệu không tồn tại hoặc đã bị xóa!")
                            continue

                        # Hiển thị thông tin tài liệu hiện tại
                        print("\nThông tin tài liệu hiện tại:")
                        print("---------------------------------------------")
                        print(f"Mã tài liệu: {document['doc_id']}")
                        print(f"Tiêu đề: {document['title']}")
                        print(f"Lĩnh vực: {document['category']}")
                        print(f"Số lượng: {document['SoLuong']}")
                        print(f"Đặc biệt: {'Có' if document['DacBiet'] else 'Không'}")
                        print(f"Số lượng hiện có: {document['AvailableQuantity']}")
                        print(f"Trạng thái: {document['status']}")
                        print("---------------------------------------------")

                        # Nhập thông tin mới
                        title = get_optional_input(f"Tiêu đề ({document['title']}): ")
                        category = get_optional_input(f"Lĩnh vực ({document['category']}): ")
                        SoLuong = get_optional_input(f"Số lượng ({document['SoLuong']}): ")
                        DacBiet = get_yes_no_input(f"Đặc biệt (Y/N, hiện tại: {'Y' if document['DacBiet'] else 'N'}): ")

                        # Tạo dictionary updates
                        updates = {}
                        if title:
                            updates['title'] = title
                        if category:
                            updates['category'] = category
                        if SoLuong:
                            try:
                                updates['SoLuong'] = int(SoLuong)
                            except ValueError:
                                print("Số lượng phải là số nguyên!")
                                continue
                        if DacBiet:
                            updates['DacBiet'] = DacBiet.lower() == 'y'

                        # Nếu không có thay đổi, bỏ qua
                        if not updates:
                            print("Không có thông tin nào được cập nhật!")
                            continue

                        # Xác nhận trước khi cập nhật
                        confirm = get_yes_no_input("Bạn có chắc chắn muốn cập nhật tài liệu này (Y/N)? ")
                        if confirm.lower() != 'y':
                            print("Hủy thao tác cập nhật.")
                            continue

                        # Gọi phương thức update_document
                        doc_manager.update_document(doc_id, updates)

                        # Hiển thị thông tin sau khi cập nhật
                        updated_doc = doc_manager.get_document_details(doc_id)
                        print("\nCập nhật thông tin tài liệu thành công!")
                        print("---------------------------------------------")
                        print(f"Mã tài liệu: {updated_doc['doc_id']}")
                        print(f"Tiêu đề: {updated_doc['title']}")
                        print(f"Lĩnh vực: {updated_doc['category']}")
                        print(f"Số lượng: {updated_doc['SoLuong']}")
                        print(f"Đặc biệt: {'Có' if updated_doc['DacBiet'] else 'Không'}")
                        print(f"Số lượng hiện có: {updated_doc['AvailableQuantity']}")
                        print(f"Trạng thái: {updated_doc['status']}")
                        print("---------------------------------------------")

                    except ValueError as e:
                        print(f"Lỗi cập nhật: {e}")

                elif sub_choice == "7":  # Khôi phục tài liệu
                    # Hiển thị danh sách tài liệu đã xóa
                    deleted_docs = [doc for doc in doc_manager.documents if doc.get('deleted', False)]
                    if not deleted_docs:
                        print("Không có tài liệu nào đã bị xóa!")
                        continue

                    print("\nDanh sách tài liệu đã xóa:")
                    print("---------------------------------------------")
                    for doc in deleted_docs:
                        print(f"Mã tài liệu: {doc['doc_id']}")
                        print(f"Tiêu đề: {doc['title']}")
                        print(f"Lĩnh vực: {doc['category']}")
                        print(f"Số lượng: {doc['SoLuong']}")
                        print("---------------------------------------------")

                    try:
                        doc_id = get_non_empty_input("Nhập mã tài liệu đã xóa: ")
        
                        # Kiểm tra tài liệu tồn tại (bao gồm cả tài liệu đã xóa)
                        document = doc_manager.get_document_details(doc_id, include_deleted=True)
                        if not document:
                            print("Tài liệu không tồn tại!")
                            continue

                        # Hiển thị thông tin chi tiết tài liệu
                        print("\nThông tin tài liệu:")
                        print("---------------------------------------------")
                        print(f"Mã tài liệu: {document['doc_id']}")
                        print(f"Tiêu đề: {document['title']}")
                        print(f"Lĩnh vực: {document['category']}")
                        print(f"Số lượng: {document['SoLuong']}")
                        print(f"Đặc biệt: {'Có' if document['DacBiet'] else 'Không'}")
                        print(f"Trạng thái: {'Đã xóa' if document.get('deleted', False) else 'Chưa xóa'}")
                        print(f"Số lượng hiện có: {document['AvailableQuantity']}")
                        print("---------------------------------------------")

                        # Xác nhận trước khi khôi phục
                        confirm = get_yes_no_input("Bạn có chắc chắn muốn khôi phục tài liệu này (Y/N)? ")
                        if confirm.lower() != 'y':
                            print("Hủy thao tác khôi phục.")
                            continue

                        # Gọi phương thức khôi phục
                        doc_manager.restore_document(doc_id)

                        # Hiển thị thông tin sau khi khôi phục
                        document = doc_manager.get_document_details(doc_id)
                        print("\nKhôi phục tài liệu thành công!")
                        print("---------------------------------------------")
                        print(f"Mã tài liệu: {document['doc_id']}")
                        print(f"Tiêu đề: {document['title']}")
                        print(f"Trạng thái: {'Đã xóa' if document.get('deleted', False) else 'Chưa xóa'}")
                        print("---------------------------------------------")

                    except ValueError as e:
                        print(f"Lỗi khôi phục tài liệu: {e}")

                elif sub_choice == "8":  # Quay lại
                    break

                else:
                    print("Lựa chọn không hợp lệ. Vui lòng chọn lại.")

        elif choice == "3":  # Quản lý phiếu mượn
            while True:
                print("\n=== QUẢN LÝ PHIẾU MƯỢN ===")
                print("1. Lập phiếu mượn")
                print("2. Tìm kiếm phiếu mượn")
                print("3. Xem phiếu mượn quá hạn")
                print("4. Xem tất cả phiếu mượn chưa trả")
                print("5. Xem/Chỉnh sửa/Xóa phiếu mượn")
                print("6. Gia hạn thời gian mượn")  # Mới
                print("7. Quản lý đặt trước tài liệu")  # Mới
                print("8. Quay lại")
                sub_choice = input("Chọn chức năng (1-8): ").strip()

                if sub_choice == "1":  # Lập phiếu mượn
                    try:
                        reader_id = get_non_empty_input("Nhập mã độc giả: ")
                        doc_ids_input = get_non_empty_input("Nhập danh sách mã tài liệu (cách nhau bởi dấu phẩy, ví dụ: TL001,TL002): ")
                        doc_ids = [doc_id.strip() for doc_id in doc_ids_input.split(",")]
                        borrow_record = borrowing_manager.create_borrow_record(
                            reader_id, doc_ids, reader_manager, doc_manager
                        )
                        print(f"Lập phiếu mượn thành công! Mã phiếu: {borrow_record['borrow_id']}")
                    except ValueError as e:
                        print(f"Lỗi lập phiếu mượn: {e}")

                elif sub_choice == "2":  # Tìm kiếm phiếu mượn
                    borrow_id = get_optional_input("Nhập mã phiếu mượn (nhấn Enter nếu không tìm theo mã): ")
                    reader_id = get_optional_input("Nhập mã độc giả (nhấn Enter nếu không tìm theo mã): ")
                    results = borrowing_manager.search_borrow_records(borrow_id=borrow_id, reader_id=reader_id)
                    if results:
                        print("\nKết quả tìm kiếm:")
                        for result in results:
                            print(result)
                        while True:
                            print("\n=== TÙY CHỌN KẾT QUẢ TÌM KIẾM ===")
                            print("1. Xem chi tiết phiếu mượn")
                            print("2. Xóa phiếu mượn")
                            print("3. Lập phiếu trả")
                            print("4. Gia hạn mượn")  # Mới
                            print("5. Quay lại")
                            action_choice = input("Chọn hành động (1-5): ").strip()

                            if action_choice == "1":  # Xem chi tiết phiếu mượn
                                borrow_id = get_non_empty_input("Nhập mã phiếu mượn: ")
                                record = borrowing_manager.get_borrow_record_details(borrow_id)
                                if record:
                                    print("\nChi tiết phiếu mượn:")
                                    print(record)
                                else:
                                    print("Không tìm thấy phiếu mượn.")

                            elif action_choice == "2":  # Xóa phiếu mượn
                                try:
                                    borrow_id = get_non_empty_input("Nhập mã phiếu mượn: ")
                                    borrowing_manager.delete_borrow_record(borrow_id, reader_manager, doc_manager)
                                    print("Xóa phiếu mượn thành công!")
                                except ValueError as e:
                                    print(f"Lỗi xóa phiếu mượn: {e}")

                            elif action_choice == "3":  # Lập phiếu trả
                                try:
                                    borrow_id = get_non_empty_input("Nhập mã phiếu mượn: ")
                                    doc_ids_input = get_non_empty_input("Nhập danh sách mã tài liệu trả (cách nhau bởi dấu phẩy): ")
                                    doc_ids = [doc_id.strip() for doc_id in doc_ids_input.split(",")]
                                    return_record = borrowing_manager.create_return_record(
                                        borrow_id, doc_ids, reader_manager, doc_manager
                                    )
                                    print(f"Lập phiếu trả thành công! Mã phiếu trả: {return_record['return_id']}")
                                    if return_record['total_fine'] > 0:
                                        print(f"Phí phạt: {return_record['total_fine']} VNĐ")
                                except ValueError as e:
                                    print(f"Lỗi lập phiếu trả: {e}")

                            elif action_choice == "4":  # Gia hạn mượn (Mới)
                                try:
                                    borrow_id = get_non_empty_input("Nhập mã phiếu mượn: ")
                                    if borrowing_manager.extend_borrow_period(borrow_id, reader_manager):
                                        record = borrowing_manager.get_borrow_record_details(borrow_id)
                                        print(f"Gia hạn thành công! Ngày hết hạn mới: {record['due_date']}")
                                except ValueError as e:
                                    print(f"Lỗi gia hạn: {e}")

                            elif action_choice == "5":  # Quay lại
                                break

                            else:
                                print("Lựa chọn không hợp lệ. Vui lòng chọn lại.")
                    else:
                        print("Không tìm thấy phiếu mượn phù hợp.")

                elif sub_choice == "3":  # Xem phiếu mượn quá hạn
                    overdue_records = borrowing_manager.get_overdue_borrow_records()
                    if overdue_records:
                        print("\nDanh sách phiếu mượn quá hạn:")
                        for record in overdue_records:
                            print(record)
                    else:
                        print("Không có phiếu mượn nào quá hạn.")

                elif sub_choice == "4":  # Xem tất cả phiếu mượn chưa trả
                    unreturned_records = borrowing_manager.get_unreturned_borrow_records()
                    if unreturned_records:
                        print("\nDanh sách phiếu mượn chưa trả:")
                        for record in unreturned_records:
                            print(record)
                    else:
                        print("Không có phiếu mượn nào chưa trả.")

                elif sub_choice == "5":  # Xem/Chỉnh sửa/Xóa phiếu mượn
                    borrow_id = get_non_empty_input("Nhập mã phiếu mượn: ")
                    record = borrowing_manager.get_borrow_record_details(borrow_id)
                    if not record:
                        print("Không tìm thấy phiếu mượn.")
                        continue

                    print("\nChi tiết phiếu mượn:")
                    print(record)
                    print("\n1. Cập nhật phiếu mượn")
                    print("2. Xóa phiếu mượn")
                    print("3. Gia hạn mượn")  
                    print("4. Quay lại")
                    action_choice = input("Chọn hành động (1-4): ").strip()

                    if action_choice == "1":  # Cập nhật phiếu mượn
                        try:
                            doc_ids_input = get_non_empty_input("Nhập danh sách mã tài liệu mới (cách nhau bởi dấu phẩy): ")
                            new_doc_ids = [doc_id.strip() for doc_id in doc_ids_input.split(",")]
                            borrowing_manager.update_borrow_record(borrow_id, new_doc_ids, reader_manager, doc_manager)
                            print("Cập nhật phiếu mượn thành công!")
                        except ValueError as e:
                            print(f"Lỗi cập nhật phiếu mượn: {e}")

                    elif action_choice == "2":  # Xóa phiếu mượn
                        try:
                            borrowing_manager.delete_borrow_record(borrow_id, reader_manager, doc_manager)
                            print("Xóa phiếu mượn thành công!")
                        except ValueError as e:
                            print(f"Lỗi xóa phiếu mượn: {e}")

                    elif action_choice == "3":  # Gia hạn mượn (Mới)
                        try:
                            if borrowing_manager.extend_borrow_period(borrow_id, reader_manager):
                                record = borrowing_manager.get_borrow_record_details(borrow_id)
                                print(f"Gia hạn thành công! Ngày hết hạn mới: {record['due_date']}")
                        except ValueError as e:
                            print(f"Lỗi gia hạn: {e}")

                    elif action_choice == "4":  # Quay lại
                        continue

                    else:
                        print("Lựa chọn không hợp lệ. Vui lòng chọn lại.")

                elif sub_choice == "6":  # Gia hạn thời gian mượn (Mới)
                    try:
                        borrow_id = get_non_empty_input("Nhập mã phiếu mượn: ")
                        if borrowing_manager.extend_borrow_period(borrow_id, reader_manager):
                            record = borrowing_manager.get_borrow_record_details(borrow_id)
                            print(f"Gia hạn thành công! Ngày hết hạn mới: {record['due_date']}")
                    except ValueError as e:
                        print(f"Lỗi gia hạn: {e}")

                elif sub_choice == "7":  # Cập nhật thông tin tài liệu
                    try:
                        doc_id = get_non_empty_input("Nhập mã tài liệu cần cập nhật: ")

                        # Kiểm tra tài liệu tồn tại
                        document = doc_manager.get_document_details(doc_id)
                        if not document:
                            print("Tài liệu không tồn tại!")
                            continue

                        # Hiển thị thông tin tài liệu hiện tại
                        print("\nThông tin tài liệu hiện tại:")
                        print("---------------------------------------------")
                        print(f"Mã tài liệu: {document['doc_id']}")
                        print(f"Tiêu đề: {document['title']}")
                        print(f"Lĩnh vực: {document['category']}")
                        print(f"Số lượng: {document['SoLuong']}")
                        print(f"Đặc biệt: {'Có' if document['DacBiet'] else 'Không'}")
                        print(f"Số lượng hiện có: {document['AvailableQuantity']}")
                        print(f"Trạng thái: {document['status']}")
                        print("---------------------------------------------")

                        # Nhập thông tin mới
                        title = get_optional_input(f"Tiêu đề ({document['title']}): ")
                        category = get_optional_input(f"Lĩnh vực ({document['category']}): ")
                        SoLuong = get_optional_input(f"Số lượng ({document['SoLuong']}): ")
                        DacBiet = get_yes_no_input(f"Đặc biệt (Y/N, hiện tại: {'Y' if document['DacBiet'] else 'N'}): ")

                        # Tạo dictionary updates
                        updates = {}
                        if title:
                            updates['title'] = title
                        if category:
                            updates['category'] = category
                        if SoLuong:
                            try:
                                updates['SoLuong'] = int(SoLuong)
                            except ValueError:
                                print("Số lượng phải là số nguyên!")
                                continue
                        if DacBiet:
                            updates['DacBiet'] = DacBiet.lower() == 'y'

                        # Nếu không có thay đổi, bỏ qua
                        if not updates:
                            print("Không có thông tin nào được cập nhật!")
                            continue

                        # Xác nhận trước khi cập nhật
                        confirm = get_yes_no_input("Bạn có chắc chắn muốn cập nhật tài liệu này (Y/N)? ")
                        if confirm.lower() != 'y':
                            print("Hủy thao tác cập nhật.")
                            continue

                        # Gọi phương thức update_document
                        doc_manager.update_document(doc_id, updates)

                        # Hiển thị thông tin sau khi cập nhật
                        updated_doc = doc_manager.get_document_details(doc_id)
                        print("\nCập nhật thông tin tài liệu thành công!")
                        print("---------------------------------------------")
                        print(f"Mã tài liệu: {updated_doc['doc_id']}")
                        print(f"Tiêu đề: {updated_doc['title']}")
                        print(f"Lĩnh vực: {updated_doc['category']}")
                        print(f"Số lượng: {updated_doc['SoLuong']}")
                        print(f"Đặc biệt: {'Có' if updated_doc['DacBiet'] else 'Không'}")
                        print(f"Số lượng hiện có: {updated_doc['AvailableQuantity']}")
                        print(f"Trạng thái: {updated_doc['status']}")
                        print("---------------------------------------------")

                    except ValueError as e:
                        print(f"Lỗi cập nhật: {e}")

                elif sub_choice == "8":  # Khôi phục tài liệu
                    # Đoạn mã cho khôi phục tài liệu (đã được cải tiến trước đó)
                    pass

                elif sub_choice == "9":  # Quay lại
                    break

                else:
                    print("Lựa chọn không hợp lệ. Vui lòng chọn lại.")

        elif choice == "4":  # Quản lý phiếu trả
            while True:
                print("\n=== QUẢN LÝ PHIẾU TRẢ ===")
                print("1. Lập phiếu trả")
                print("2. Tìm kiếm phiếu trả")
                print("3. Xem tất cả phiếu trả")
                print("4. Xem/Chỉnh sửa/Xóa phiếu trả")
                print("5. Quay lại")
                sub_choice = input("Chọn chức năng (1-5): ").strip()

                if sub_choice == "1":  # Lập phiếu trả
                    try:
                        borrow_id = get_non_empty_input("Nhập mã phiếu mượn: ")
                        doc_ids_input = get_non_empty_input("Nhập danh sách mã tài liệu trả (cách nhau bởi dấu phẩy): ")
                        doc_ids = [doc_id.strip() for doc_id in doc_ids_input.split(",")]
                        return_record = borrowing_manager.create_return_record(
                            borrow_id, doc_ids, reader_manager, doc_manager
                        )
                        print(f"Lập phiếu trả thành công! Mã phiếu trả: {return_record['return_id']}")
                        if return_record['total_fine'] > 0:
                            print(f"Phí phạt: {return_record['total_fine']} VNĐ")
                    except ValueError as e:
                        print(f"Lỗi lập phiếu trả: {e}")

                elif sub_choice == "2":  # Tìm kiếm phiếu trả
                    return_id = get_optional_input("Nhập mã phiếu trả (nhấn Enter nếu không tìm theo mã): ")
                    borrow_id = get_optional_input("Nhập mã phiếu mượn (nhấn Enter nếu không tìm theo mã): ")
                    reader_id = get_optional_input("Nhập mã độc giả (nhấn Enter nếu không tìm theo mã): ")
                    results = borrowing_manager.search_return_records(
                        return_id=return_id, borrow_id=borrow_id, reader_id=reader_id
                    )
                    if results:
                        print("\nKết quả tìm kiếm:")
                        for result in results:
                            print(result)
                        while True:
                            print("\n=== TÙY CHỌN KẾT QUẢ TÌM KIẾM ===")
                            print("1. Xem chi tiết phiếu trả")
                            print("2. Xóa phiếu trả")
                            print("3. Quay lại")
                            action_choice = input("Chọn hành động (1-3): ").strip()

                            if action_choice == "1":  # Xem chi tiết phiếu trả
                                return_id = get_non_empty_input("Nhập mã phiếu trả: ")
                                record = borrowing_manager.get_return_record_details(return_id)
                                if record:
                                    print("\nChi tiết phiếu trả:")
                                    print(record)
                                else:
                                    print("Không tìm thấy phiếu trả.")

                            elif action_choice == "2":  # Xóa phiếu trả
                                try:
                                    return_id = get_non_empty_input("Nhập mã phiếu trả: ")
                                    borrowing_manager.delete_return_record(return_id, reader_manager, doc_manager)
                                    print("Xóa phiếu trả thành công!")
                                except ValueError as e:
                                    print(f"Lỗi xóa phiếu trả: {e}")

                            elif action_choice == "3":  # Quay lại
                                break

                            else:
                                print("Lựa chọn không hợp lệ. Vui lòng chọn lại.")
                    else:
                        print("Không tìm thấy phiếu trả phù hợp.")

                elif sub_choice == "3":  # Xem tất cả phiếu trả
                    all_records = borrowing_manager.get_all_return_records()
                    if all_records:
                        print("\nDanh sách tất cả phiếu trả:")
                        for record in all_records:
                            print(record)
                    else:
                        print("Không có phiếu trả nào.")

                elif sub_choice == "4":  # Xem/Chỉnh sửa/Xóa phiếu trả
                    return_id = get_non_empty_input("Nhập mã phiếu trả: ")
                    record = borrowing_manager.get_return_record_details(return_id)
                    if not record:
                        print("Không tìm thấy phiếu trả.")
                        continue

                    print("\nChi tiết phiếu trả:")
                    print(record)
                    print("\n1. Cập nhật phiếu trả")
                    print("2. Xóa phiếu trả")
                    print("3. Quay lại")
                    action_choice = input("Chọn hành động (1-3): ").strip()

                    if action_choice == "1":  # Cập nhật phiếu trả
                        try:
                            doc_ids_input = get_non_empty_input("Nhập danh sách mã tài liệu trả mới (cách nhau bởi dấu phẩy): ")
                            new_doc_ids = [doc_id.strip() for doc_id in doc_ids_input.split(",")]
                            borrowing_manager.update_return_record(return_id, new_doc_ids, reader_manager, doc_manager)
                            print("Cập nhật phiếu trả thành công!")
                        except ValueError as e:
                            print(f"Lỗi cập nhật phiếu trả: {e}")

                    elif action_choice == "2":  # Xóa phiếu trả
                        try:
                            borrowing_manager.delete_return_record(return_id, reader_manager, doc_manager)
                            print("Xóa phiếu trả thành công!")
                        except ValueError as e:
                            print(f"Lỗi xóa phiếu trả: {e}")

                    elif action_choice == "3":  # Quay lại
                        continue

                    else:
                        print("Lựa chọn không hợp lệ. Vui lòng chọn lại.")

                elif sub_choice == "5":  # Quay lại
                    break

                else:
                    print("Lựa chọn không hợp lệ. Vui lòng chọn lại.")

        elif choice == "5":  # Thống kê
            while True:
                print("\n=== THỐNG KÊ ===")
                print("1. Thống kê tổng số tài liệu")
                print("2. Thống kê tài liệu đã mượn")
                print("3. Thống kê mượn sách của độc giả")
                print("4. Thống kê độc giả mượn nhiều nhất")
                print("5. Thống kê tỷ lệ mượn sách theo loại độc giả")
                print("6. Thống kê phí phạt")
                print("7. Quay lại")
                sub_choice = input("Chọn chức năng (1-7): ").strip()

                if sub_choice == "1":  # Thống kê tổng số tài liệu
                    stats = doc_manager.get_document_stats()
                    print("\nThống kê tổng số tài liệu:")
                    print("Theo tiêu đề:")
                    for title, count in stats['by_title'].items():
                        print(f"{title}: {count} (tổng số lượng)")
                    print("\nTheo lĩnh vực:")
                    for category, count in stats['by_category'].items():
                        print(f"{category}: {count} (tổng số lượng)")
                    print("\nTheo trạng thái:")
                    for status, count in stats['by_status'].items():
                        print(f"Trạng thái {status}: {count} (tổng số lượng)")
                    print("\nTheo đặc biệt:")
                    for DacBiet, count in stats['by_DacBiet'].items():
                        print(f"Đặc biệt ({DacBiet}): {count} (tổng số lượng)")

                elif sub_choice == "2":  # Thống kê tài liệu đã mượn
                    stats = doc_manager.get_borrowed_documents_stats(reader_manager.readers)
                    print("\nThống kê tài liệu đã mượn:")
                    print("Theo tiêu đề:")
                    for title, count in stats['by_title'].items():
                        print(f"{title}: {count} (đã mượn)")
                    print("\nTheo lĩnh vực:")
                    for category, count in stats['by_category'].items():
                        print(f"{category}: {count} (đã mượn)")

                elif sub_choice == "3":  # Thống kê mượn sách của độc giả
                    stats = reader_manager.get_borrowing_stats()
                    print("\nThống kê mượn sách:")
                    print(stats)

                elif sub_choice == "4":  # Thống kê độc giả mượn nhiều nhất
                    top_borrowers = reader_manager.get_top_borrowers()
                    print("\nDanh sách độc giả mượn nhiều nhất:")
                    for borrower in top_borrowers:
                        print(borrower)

                elif sub_choice == "5":  # Thống kê tỷ lệ mượn sách theo loại độc giả
                    ratios = reader_manager.get_reader_type_borrowing_ratio()
                    print("\nTỷ lệ mượn sách theo loại độc giả:")
                    for reader_type, data in ratios.items():
                        print(f"{reader_type}: {data['books']} sách ({data['percentage']:.2f}%)")

                elif sub_choice == "6":  # Thống kê phí phạt
                    readers_with_fines = reader_manager.get_readers_with_fines()
                    if readers_with_fines:
                        print("\nDanh sách độc giả có phí phạt:")
                        for reader in readers_with_fines:
                            print(reader)
                    else:
                        print("Không có độc giả nào có phí phạt.")

                elif sub_choice == "7":  # Quay lại
                    break

                else:
                    print("Lựa chọn không hợp lệ. Vui lòng chọn lại.")

        elif choice == "6":  # Thoát
            print("Tạm biệt!")
            break

        else:
            print("Lựa chọn không hợp lệ. Vui lòng chọn lại.")
