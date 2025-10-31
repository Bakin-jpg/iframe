# test_full_series_scraper.py

from playwright.sync_api import sync_playwright, TimeoutError
import json
import time

def scrape_all_episodes_from_show(show_url):
    """
    Mengunjungi halaman utama sebuah anime, menemukan semua episodenya,
    dan mengambil URL iframe dari masing-masing episode.
    """
    print("="*50)
    print("   MEMULAI PENGUJIAN SCRAPER UNTUK SEMUA EPISODE   ")
    print("="*50)
    print(f"URL Halaman Anime: {show_url}\n")
    
    episodes_data = []

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # 1. Buka halaman utama anime
            print(f"1. Menavigasi ke halaman utama anime...")
            page.goto(show_url, timeout=90000)
            print("   Halaman utama berhasil dimuat.")

            # 2. Tunggu dan dapatkan daftar semua elemen episode
            episode_item_selector = "div.episode-item"
            print(f"2. Menunggu daftar episode muncul dengan selector: '{episode_item_selector}'...")
            page.wait_for_selector(episode_item_selector, timeout=60000)
            
            episode_locators = page.locator(episode_item_selector)
            episode_count = episode_locators.count()
            print(f"   Ditemukan {episode_count} episode di halaman ini.")
            
            # 3. Looping untuk setiap episode
            for i in range(episode_count):
                print(f"\n--- Memproses Episode {i + 1} dari {episode_count} ---")
                
                # Re-locate elemen di setiap iterasi untuk menghindari 'stale element' error
                all_episodes = page.locator(episode_item_selector)
                current_episode_element = all_episodes.nth(i)

                # Ambil nomor episode sebelum mengklik
                episode_number_text = current_episode_element.locator("span.v-chip__content").inner_text()
                print(f"   Nomor Episode: {episode_number_text}")

                # Klik pada elemen episode untuk navigasi
                print("   Mengklik link episode...")
                current_episode_element.click()

                # Tunggu halaman episode baru termuat
                page.wait_for_load_state('networkidle', timeout=60000)
                episode_url = page.url
                print(f"   Berhasil menavigasi ke: {episode_url}")
                
                # Ambil iframe dari halaman episode
                iframe_src = None
                try:
                    iframe_selector = "div.player-container iframe.player"
                    print(f"   Mencari iframe...")
                    page.wait_for_selector(iframe_selector, timeout=30000)
                    iframe_element = page.locator(iframe_selector)
                    iframe_src = iframe_element.get_attribute('src')
                    print(f"   Iframe ditemukan: {iframe_src}")
                except TimeoutError:
                    print("   [PERINGATAN] Iframe tidak ditemukan untuk episode ini dalam 30 detik.")
                    iframe_src = "Not Found"

                # Simpan data yang didapat
                episodes_data.append({
                    "episode_number": episode_number_text,
                    "episode_url": episode_url,
                    "iframe_url": iframe_src
                })
                
                # Kembali ke halaman utama untuk loop selanjutnya
                print("   Kembali ke halaman daftar episode...")
                page.go_back()
                page.wait_for_load_state('networkidle', timeout=60000)

            print("\n" + "="*50)
            print("Semua episode di halaman ini telah diproses.")
            browser.close()

        except Exception as e:
            print(f"\n[ERROR] Terjadi kesalahan fatal: {e}")
            if 'browser' in locals() and browser.is_connected():
                browser.close()
            raise SystemExit(f"Test Gagal: {e}")
            
    return episodes_data

if __name__ == "__main__":
    # URL Halaman Utama Anime yang akan kita uji
    # Anda bisa mengganti ini dengan URL anime lain jika perlu
    test_show_url = "https://kickass-anime.ru/potion-wagami-wo-tasukeru-f0c8"
    
    # Jalankan fungsi pengujian
    final_data = scrape_all_episodes_from_show(test_show_url)

    # Simpan hasil akhir ke file JSON
    if final_data:
        output_filename = "episode_iframes.json"
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(final_data, f, ensure_ascii=False, indent=4)
        
        print(f"\nSTATUS: BERHASIL ✅")
        print(f"Total {len(final_data)} episode diproses dan disimpan di '{output_filename}'")
    else:
        print("\nSTATUS: GAGAL ❌")
        print("Tidak ada data episode yang berhasil diambil.")
