# test_iframe_scraper.py

from playwright.sync_api import sync_playwright, TimeoutError

def test_scrape_single_iframe(episode_url):
    """
    Fungsi ini hanya bertujuan untuk menguji pengambilan URL iframe dari
    satu halaman episode.
    """
    print("="*40)
    print("   MEMULAI PENGUJIAN SCRAPER IFRAME   ")
    print("="*40)
    print(f"URL Target: {episode_url}\n")
    
    iframe_src = None

    with sync_playwright() as p:
        try:
            print("1. Meluncurkan browser Chromium (headless)...")
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            print(f"2. Menavigasi ke halaman episode...")
            page.goto(episode_url, timeout=90000, wait_until="domcontentloaded")
            print("   Halaman berhasil dimuat.")

            iframe_selector = "div.player-container iframe.player"
            
            print(f"3. Menunggu elemen iframe muncul (timeout 60 detik)...")
            page.wait_for_selector(iframe_selector, timeout=60000)
            print("   Elemen iframe ditemukan di halaman!")

            print("4. Mengambil atribut 'src' dari elemen iframe...")
            iframe_element = page.locator(iframe_selector)
            iframe_src = iframe_element.get_attribute('src')
            
            browser.close()
            print("\n5. Browser berhasil ditutup.")

        except TimeoutError:
            print("\n[ERROR] Waktu habis saat menunggu elemen iframe.")
            print("      - Mungkin selector sudah berubah atau halaman lambat.")
            if 'browser' in locals() and browser.is_connected():
                browser.close()
            # Gagal secara eksplisit agar workflow error
            raise SystemExit("Test Gagal: Timeout")
        except Exception as e:
            print(f"\n[ERROR] Terjadi kesalahan yang tidak terduga: {e}")
            if 'browser' in locals() and browser.is_connected():
                browser.close()
            # Gagal secara eksplisit agar workflow error
            raise SystemExit(f"Test Gagal: {e}")
            
    return iframe_src

if __name__ == "__main__":
    # URL yang akan kita uji
    test_url = "https://kickass-anime.ru/potion-wagami-wo-tasukeru-f0c8/ep-5-ca3332"
    
    # Jalankan fungsi pengujian
    result_url = test_scrape_single_iframe(test_url)

    # Tampilkan hasil akhir
    print("\n" + "="*40)
    print("         HASIL AKHIR PENGUJIAN         ")
    print("="*40)

    if result_url:
        print("STATUS: BERHASIL ✅")
        print(f"URL Iframe yang didapat: {result_url}")
    else:
        print("STATUS: GAGAL ❌")
        print("URL Iframe tidak dapat ditemukan.")
