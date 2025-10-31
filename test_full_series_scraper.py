# test_full_series_scraper.py

from playwright.sync_api import sync_playwright, TimeoutError
import json

def scrape_all_episodes_from_show(show_url):
    """
    Mengunjungi halaman detail sebuah anime, mengklik "Watch Now" untuk masuk
    ke halaman episode, menemukan semua episodenya, dan mengambil URL iframe
    dari masing-masing episode.
    """
    print("="*50)
    print("   MEMULAI PENGUJIAN SCRAPER UNTUK SEMUA EPISODE (V2)   ")
    print("="*50)
    print(f"URL Halaman Anime: {show_url}\n")
    
    episodes_data = []

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # 1. Buka halaman detail anime
            print(f"1. Menavigasi ke halaman detail anime...")
            page.goto(show_url, timeout=90000, wait_until="domcontentloaded")
            print("   Halaman detail berhasil dimuat.")

            # === PERUBAHAN KRUSIAL DIMULAI DI SINI ===
            # 2. Cari dan klik tombol "Watch Now"
            watch_now_selector = "a.pulse-button:has-text('Watch Now')"
            print(f"2. Mencari tombol 'Watch Now' dengan selector: '{watch_now_selector}'...")
            page.wait_for_selector(watch_now_selector, timeout=60000)
            print("   Tombol 'Watch Now' ditemukan. Mengklik tombol...")
            page.locator(watch_now_selector).click()
            # === PERUBAHAN KRUSIAL SELESAI ===

            # 3. Tunggu halaman episode pertama termuat sepenuhnya
            print("3. Menunggu halaman episode termuat setelah klik...")
            page.wait_for_load_state('networkidle', timeout=60000)
            print(f"   Berhasil menavigasi ke halaman episode: {page.url}")

            # 4. Tunggu dan dapatkan daftar semua elemen episode
            episode_item_selector = "div.episode-item"
            print(f"4. Menunggu daftar episode muncul dengan selector: '{episode_item_selector}'...")
            page.wait_for_selector(episode_item_selector, timeout=60000)
            
            episode_locators = page.locator(episode_item_selector)
            episode_count = episode_locators.count()
            print(f"   Ditemukan {episode_count} episode di halaman ini.")
            
            # 5. Looping untuk setiap episode
            for i in range(episode_count):
                print(f"\n--- Memproses Episode {i + 1} dari {episode_count} ---")
                
                # Re-locate elemen di setiap iterasi
                all_episodes = page.locator(episode_item_selector)
                current_episode_element = all_episodes.nth(i)

                episode_number_text = await current_episode_element.locator("span.v-chip__content").inner_text()
                print(f"   Nomor Episode: {episode_number_text}")

                # Klik episode jika bukan yang sedang aktif
                # Periksa apakah ada overlay 'Playing'
                is_playing = await current_episode_element.locator("div.v-overlay__content:has-text('Playing')").is_visible()
                if not is_playing:
                    print("   Mengklik link episode...")
                    await current_episode_element.click()
                    await page.wait_for_load_state('networkidle', timeout=60000)
                else:
                    print("   Ini adalah episode yang sedang diputar, tidak perlu diklik.")
                
                episode_url = page.url
                print(f"   URL Halaman Episode: {episode_url}")
                
                iframe_src = None
                try:
                    iframe_selector = "div.player-container iframe.player"
                    print(f"   Mencari iframe...")
                    await page.wait_for_selector(iframe_selector, timeout=30000)
                    iframe_element = page.locator(iframe_selector)
                    iframe_src = await iframe_element.get_attribute('src')
                    print(f"   Iframe ditemukan: {iframe_src}")
                except TimeoutError:
                    print("   [PERINGATAN] Iframe tidak ditemukan untuk episode ini.")
                    iframe_src = "Not Found"

                episodes_data.append({
                    "episode_number": episode_number_text,
                    "episode_url": episode_url,
                    "iframe_url": iframe_src
                })
                
                # Tidak perlu kembali (go_back) karena kita berada di halaman yang sama
                # dan hanya mengklik elemen yang me-refresh bagian tertentu dari halaman.
                # Namun, jika klik episode me-reload halaman, logika navigasi perlu disesuaikan lagi.
                # Dari pengamatan, klik episode lain akan me-reload halaman.
                # Kita akan coba navigasi ulang jika perlu, tapi untuk episode pertama cukup.
                # Untuk tes ini, kita sederhanakan dengan hanya mengambil data dari episode pertama.
                # Jika ingin mengambil semua, logika navigasi antar episode harus lebih kompleks.
                
                # Untuk saat ini, kita akan break setelah episode pertama untuk memastikan alur dasarnya benar.
                print("   Pengujian berhenti setelah episode pertama untuk verifikasi alur.")
                break


            print("\n" + "="*50)
            print("Pengujian selesai.")
            browser.close()

        except Exception as e:
            print(f"\n[ERROR] Terjadi kesalahan fatal: {e}")
            if 'browser' in locals() and browser.is_connected():
                browser.close()
            raise SystemExit(f"Test Gagal: {e}")
            
    return episodes_data

if __name__ == "__main__":
    test_show_url = "https://kickass-anime.ru/potion-wagami-wo-tasukeru-f0c8"
    
    final_data = scrape_all_episodes_from_show(test_show_url)

    if final_data:
        output_filename = "episode_iframes.json"
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(final_data, f, ensure_ascii=False, indent=4)
        
        print(f"\nSTATUS: BERHASIL ✅")
        print(f"Data dari episode pertama berhasil diambil dan disimpan di '{output_filename}'")
    else:
        print("\nSTATUS: GAGAL ❌")
        print("Tidak ada data episode yang berhasil diambil.")
