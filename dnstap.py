import os
import binascii

# Создаем директорию для корпуса
os.makedirs("in", exist_ok=True)

# Данные для 20 dnstap-сообщений в hex-формате
dnstap_corpus = [
    # 1. A-запрос (example.com)
    "0a0d0801120b080110011a050001800000",
    # 2. A-ответ (example.com)
    "0a1d08021219080110011a15000180800001000100000000010001c00c00010001000000ff00047f000001",
    # 3. AAAA-запрос (ipv6.example.com)
    "0a15080112110801101c1a0d00018000000469707636076578616d706c6503636f6d00",
    # 4. AAAA-ответ (ipv6.example.com)
    "0a29080212250801101c1a2100018080000100010000000001001c0001c00c001c0001000000ff001020010db80000000000000000000001",
    # 5. MX-запрос (example.com)
    "0a0e0801120a0801100f1a060001800000",
    # 6. MX-ответ (example.com)
    "0a2b080212270801100f1a2300018080000100010000000001000f0001c00c000f0001000000ff0009000a056d61696cc00c",
    # 7. TXT-запрос (example.com)
    "0a0e0801120a080110101a060001800000",
    # 8. TXT-ответ (example.com)
    "0a2a08021226080110101a220001808000010001000000000100100001c00c00100001000000ff000c0b2248656c6c6f20576f726c6422",
    # 9. NS-запрос (example.com)
    "0a0e0801120a080110021a060001800000",
    # 10. NS-ответ (example.com)
    "0a2d08021229080110021a250001808000010002000000000100020001c00c00020001000000ff0006036e7331c00cc00c00020001000000ff0006036e7332c00c",
    # 11. SOA-запрос (example.com)
    "0a0e0801120a080110061a060001800000",
    # 12. SOA-ответ (example.com)
    "0a3d08021239080110061a350001808000010001000000000100060001c00c00060001000000ff0022036e7331c00c0561646d696ec00c7765b100000e1000000e1000000e1000000e10",
    # 13. CNAME-запрос (www.example.com)
    "0a110801120d080110051a09000180000003777777",
    # 14. CNAME-ответ (www.example.com)
    "0a200802121c080110051a180001808000010001000000000100050001c00c00050001000000ff0002c010",
    # 15. PTR-запрос (1.0.0.127.in-addr.arpa)
    "0a1d080112190801100c1a150001800000013101300130013707696e2d61646472046172706100",
    # 16. PTR-ответ (1.0.0.127.in-addr.arpa)
    "0a2a080212260801100c1a2200018080000100010000000001000c0001c00c000c0001000000ff000c076578616d706c6503636f6d00",
    # 17. ANY-запрос (example.com)
    "0a0e0801120a080110ff1a060001800000",
    # 18. DNSTAP с дополнительными полями
    "120c0a080801100118904e20011a0b080110011a050001800000",
    # 19. Сообщение с несколькими вопросами
    "0a1608011212080110011a0e0002800000076578616d706c6503636f6d00",
    # 20. Пустое сообщение (edge case)
    "0a00"
]

# Генерируем файлы
for i, hex_data in enumerate(dnstap_corpus, 1):
    filename = os.path.join("in", f"{i}.dnstap")
    binary_data = binascii.unhexlify(hex_data)
    
    with open(filename, "wb") as f:
        f.write(binary_data)
    
    print(f"Created: {filename} ({len(binary_data)} bytes)")

print("\nCorpus generation complete. 20 files created in 'in/' directory.")
