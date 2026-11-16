"""
Animasi Proses Klasifikasi Kesesuaian Lahan
Untuk Seminar — Data & Alur Sesuai Aplikasi

Alur Lengkap:
1. Upload ZIP Shapefile
2. Ekstraksi Atribut (GDAL/OGR)
3. Load Kriteria dari Database
4. Parse Multi-Range Kriteria (string → tuple kondisi)
5. Transformasi Nilai (nilai mentah → skor)
6. Skoring & Klasifikasi (Metode Faktor Pembatas / Minimum Method)
7. Statistik Hasil Kesesuaian (bar chart)

Cara pakai:
    pip install manim
    manim -pql classification_animation.py ClassificationScene
"""

from manim import *

# ── Warna konsisten (sama dengan CLASS_COLORS di aplikasi web) ──
C_S1 = "#1a9641"
C_S2 = "#a6d96a"
C_S3 = "#fdae61"
C_N = "#d7191c"
C_UNKNOWN = "#9ca3af"
C_BG = "#1e1e2e"
C_GRID = "#4b5563"

CLASS_COLORS = {"S1": C_S1, "S2": C_S2, "S3": C_S3, "N": C_N, "Unknown": C_UNKNOWN}

# Area aman (frame Manim default: 14.22 x 8)
SAFE_W = 13.0


# ══════════════════════════════════════════════
# HELPER FUNCTIONS (layout)
# ══════════════════════════════════════════════
def ml_text(text, font_size=20, color=WHITE, weight=NORMAL, line_buff=0.06):
    """Text multi-baris yang rata TENGAH (Text biasa rata kiri)."""
    lines = text.split("\n")
    if len(lines) == 1:
        return Text(text, font_size=font_size, color=color, weight=weight)
    return VGroup(
        *[Text(l, font_size=font_size, color=color, weight=weight) for l in lines]
    ).arrange(DOWN, buff=line_buff)


def fit(mob, max_w=None, max_h=None):
    """Perkecil mobject (jika perlu) agar muat di kotak max_w x max_h."""
    if max_w is not None and mob.width > max_w:
        mob.scale_to_fit_width(max_w)
    if max_h is not None and mob.height > max_h:
        mob.scale_to_fit_height(max_h)
    return mob


def boxed(content, color, buff=0.3):
    """Bungkus konten dengan kotak yang ukurannya otomatis mengikuti isi."""
    box = SurroundingRectangle(content, color=color, buff=buff, stroke_width=2)
    box.set_fill(color, 0.1)
    return VGroup(box, content)


def arrow_with_label(label, color, length=1.2, font_size=16):
    """Panah horizontal dengan label di atasnya. Index 0 = label, 1 = panah."""
    arrow = Arrow(LEFT * length / 2, RIGHT * length / 2, buff=0, color=color, stroke_width=6)
    lbl = ml_text(label, font_size, color)
    return VGroup(lbl, arrow).arrange(DOWN, buff=0.12)


def make_table(data, col_colors, font_size=20, pad_x=0.25, pad_y=0.1):
    """
    Tabel dengan kolom RATA (lebar kolom = sel terlebar) dan tinggi baris
    menyesuaikan isi (mendukung sel multi-baris).
    Return: VGroup of rows. Tiap row = VGroup(bg_rect, *cells).
    """
    n_rows, n_cols = len(data), len(data[0])
    cells = [
        [
            ml_text(
                data[r][c],
                font_size,
                col_colors[c],
                BOLD if r == 0 else NORMAL,
            )
            for c in range(n_cols)
        ]
        for r in range(n_rows)
    ]
    col_w = [max(cells[r][c].width for r in range(n_rows)) + 2 * pad_x for c in range(n_cols)]
    row_h = [max(cells[r][c].height for c in range(n_cols)) + 2 * pad_y for r in range(n_rows)]
    total_w = sum(col_w)

    rows = VGroup()
    y = 0.0
    for r in range(n_rows):
        bg = Rectangle(width=total_w, height=row_h[r])
        bg.set_stroke(C_GRID, 1)
        bg.set_fill(WHITE, 0.08 if r == 0 else 0)
        bg.move_to([total_w / 2, -(y + row_h[r] / 2), 0])

        x = 0.0
        for c in range(n_cols):
            cells[r][c].move_to([x + col_w[c] / 2, -(y + row_h[r] / 2), 0])
            x += col_w[c]

        rows.add(VGroup(bg, *cells[r]))
        y += row_h[r]

    rows.move_to(ORIGIN)
    return rows


def highlight_row(table, row_idx, color):
    """Highlight satu baris (pakai background rect baris itu)."""
    h = table[row_idx][0].copy()
    h.set_stroke(color, 3)
    h.set_fill(color, 0.18)
    return h


def color_scores(table):
    """Warnai kolom terakhir (S1/S2/S3/N) sesuai kelasnya."""
    for row in table[1:]:
        cell = row[-1]
        cell.set_color(CLASS_COLORS.get(cell.text, WHITE))


def make_result_chip(raw_val, result_class, result_color):
    """Chip hasil transformasi: nilai → kelas."""
    raw = Text(raw_val, font_size=18, color=BLUE)
    arr = Text("→", font_size=18, color=YELLOW)
    res = Text(result_class, font_size=22, color=result_color, weight=BOLD)
    row = VGroup(raw, arr, res).arrange(RIGHT, buff=0.15)
    box = SurroundingRectangle(row, color=result_color, buff=0.14, stroke_width=2)
    box.set_fill(result_color, 0.1)
    return VGroup(box, row)


def make_formula(font_size=26, color=WHITE):
    """C_akhir = min(C₁, C₂, C₃, …, Cₙ) — tanpa LaTeX (subskrip dibuat manual)."""
    c = Text("C", font_size=font_size, color=color)
    sub = Text("akhir", font_size=int(font_size * 0.55), color=color)
    sub.next_to(c, RIGHT, buff=0.03).shift(DOWN * 0.1)
    left = VGroup(c, sub)
    right = Text("= min(C₁, C₂, C₃, …, Cₙ)", font_size=font_size, color=color)
    right.next_to(left, RIGHT, buff=0.15)
    return VGroup(left, right)


class ClassificationScene(Scene):
    def setup(self):
        self.camera.background_color = C_BG

    def clear_scene(self, run_time=0.6):
        """Hapus SEMUA objek di layar (menghindari sisa objek antar-scene)."""
        if self.mobjects:
            self.play(*[FadeOut(m) for m in self.mobjects], run_time=run_time)

    def reveal_arrow(self, arrow_group, run_time=0.6):
        self.play(GrowArrow(arrow_group[1]), FadeIn(arrow_group[0]), run_time=run_time)

    # ══════════════════════════════════════════════
    # 1. TITLE SLIDE
    # ══════════════════════════════════════════════
    def title_slide(self):
        title = Text(
            "Klasifikasi Kesesuaian Lahan",
            font_size=44,
            weight=BOLD,
            color=BLUE,
        )
        subtitle = Text(
            "Metode Faktor Pembatas — Evaluasi Kesesuaian Lahan",
            font_size=26,
            color=GRAY_C,
        )
        group = VGroup(title, subtitle).arrange(DOWN, buff=0.4).move_to(ORIGIN)

        self.play(Write(title), run_time=1.2)
        self.play(FadeIn(subtitle, shift=UP * 0.2), run_time=0.8)
        self.wait(1.5)
        self.play(FadeOut(group, shift=UP * 0.3))

    # ══════════════════════════════════════════════
    # 2. PIPELINE OVERVIEW (6 tahap)
    # ══════════════════════════════════════════════
    def pipeline_overview(self):
        stages = [
            ("Upload\nZIP", BLUE),
            ("Ekstrak\nShapefile", TEAL),
            ("Load\nKriteria", PURPLE),
            ("Parse\nMulti-Range", YELLOW),
            ("Skoring &\nKlasifikasi", ORANGE),
            ("Peta\nKesesuaian", GREEN),
        ]

        boxes = VGroup()
        for label, color in stages:
            rect = RoundedRectangle(
                corner_radius=0.15, width=1.8, height=1.3, color=color, fill_opacity=0.15
            )
            txt = ml_text(label, 18, color)
            boxes.add(VGroup(rect, txt))  # rect & txt sama-sama di ORIGIN → teks tepat di tengah

        # 6 kotak disusun & ditengahkan (sebelumnya melebar keluar frame kanan)
        boxes.arrange(RIGHT, buff=0.45)
        fit(boxes, max_w=SAFE_W)
        boxes.move_to(ORIGIN)

        arrows = VGroup(
            *[
                Arrow(boxes[i].get_right(), boxes[i + 1].get_left(), buff=0.05, color=GRAY_C)
                for i in range(len(boxes) - 1)
            ]
        )

        label = Text("Pipeline Klasifikasi", font_size=28, color=GRAY_A)
        label.to_edge(UP, buff=0.6)
        self.play(Write(label), run_time=0.6)

        for i, box in enumerate(boxes):
            if i == 0:
                self.play(FadeIn(box), run_time=0.5)
            else:
                self.play(FadeIn(box), GrowArrow(arrows[i - 1]), run_time=0.5)
        self.wait(1.2)

        # Highlight "Parse Multi-Range" (tanpa teks tambahan)
        highlight_box = SurroundingRectangle(boxes[3], color=YELLOW, buff=0.1, stroke_width=4)
        self.play(Create(highlight_box))
        self.wait(1.5)

        self.clear_scene()

    # ══════════════════════════════════════════════
    # 3. UPLOAD ZIP + EKSTRAKSI SHAPEFILE
    # ══════════════════════════════════════════════
    def upload_zip(self):
        title = Text("Upload & Ekstraksi Shapefile", font_size=32, color=BLUE)
        title.to_edge(UP, buff=0.4)
        self.play(Write(title))

        zip_group = boxed(Text("Unit_Lahan_OK.zip", font_size=18, color=BLUE), BLUE)
        arr1 = arrow_with_label("Extract", TEAL, 1.0)

        files = VGroup(
            *[
                Text(f"Unit_Lahan_OK.{ext}", font_size=18, color=TEAL)
                for ext in ["shp", "dbf", "shx", "prj"]
            ]
        ).arrange(DOWN, buff=0.18, aligned_edge=LEFT)
        files_group = boxed(files, TEAL)

        arr2 = arrow_with_label("GDAL/OGR", TEAL, 1.2)

        ds_text = VGroup(
            Text("DataSource('Unit_Lahan_OK.shp')", font_size=16, color=TEAL),
            Text("Layer: Unit_Lahan_OK", font_size=16, color=TEAL),
            Text("Features: 1.247 poligon", font_size=16, color=TEAL),
            Text("Fields: 32 atribut", font_size=16, color=TEAL),
        ).arrange(DOWN, buff=0.15, aligned_edge=LEFT)
        ds_group = boxed(ds_text, TEAL)

        layout = VGroup(zip_group, arr1, files_group, arr2, ds_group).arrange(RIGHT, buff=0.3)
        fit(layout, max_w=SAFE_W)
        layout.move_to(UP * 0.4)

        self.play(FadeIn(zip_group))
        self.reveal_arrow(arr1)
        self.play(FadeIn(files_group))
        self.wait(0.8)
        self.reveal_arrow(arr2)
        self.play(FadeIn(ds_group))
        self.wait(1.5)

        summary = Text(
            "Shapefile dibaca → 1.247 fitur dengan 32 field atribut siap diproses",
            font_size=20,
            color=TEAL,
        ).to_edge(DOWN, buff=0.6)
        self.play(Write(summary))
        self.wait(1)

        self.clear_scene()

    # ══════════════════════════════════════════════
    # 4. LOAD KRITERIA DARI DATABASE
    # ══════════════════════════════════════════════
    def load_criteria(self):
        title = Text("Load Kriteria dari Database", font_size=32, color=PURPLE)
        title.to_edge(UP, buff=0.4)
        self.play(Write(title))

        db_text = VGroup(
            Text("PostgreSQL", font_size=20, color=PURPLE, weight=BOLD),
            Text("SuitabilityCharacteristic", font_size=14, color=PURPLE),
        ).arrange(DOWN, buff=0.15)
        db_group = boxed(db_text, PURPLE, buff=0.35)

        arr = arrow_with_label("Query", PURPLE, 1.2)

        query_data = [
            ["Parameter", "S1", "S2", "S3", "N"],
            ["pH Tanah", "6.0-7.0", "5.0-6.0", "4.0-5.0", "<4.0, >9.0"],
            ["C-Organik", ">2.0", "1.5-2.0", "1.0-1.5", "<1.0"],
            ["KTK", ">25.0", "17.0-25.0", "12.0-17.0", "<12.0"],
            ["Tekstur", "sedang", "halus", "kasar", "sangat_kasar"],
            ["Kedalaman", ">60", "40-60", "25-40", "<25"],
            ["Kemiringan", "0-3%", "3-8%", "8-15%", ">15%"],
        ]
        query_table = make_table(
            query_data, [BLUE, C_S1, C_S2, C_S3, C_N], font_size=16, pad_x=0.2
        )

        layout = VGroup(db_group, arr, query_table).arrange(RIGHT, buff=0.3)
        fit(layout, max_w=SAFE_W, max_h=3.3)
        layout.move_to(UP * 0.5)

        query_label = Text("Hasil Query (6 karakteristik)", font_size=16, color=PURPLE)
        query_label.next_to(query_table, UP, buff=0.15)

        self.play(FadeIn(db_group))
        self.reveal_arrow(arr)
        self.play(FadeIn(query_label), FadeIn(query_table), run_time=0.8)
        self.wait(1.5)

        note = Text("Kriteria masih berupa string mentah", font_size=24, color=YELLOW)
        note2 = Text(
            'Contoh: "6.0-7.0", "<4.0, >9.0", "sedang"', font_size=20, color=YELLOW
        )
        notes = VGroup(note, note2).arrange(DOWN, buff=0.2).move_to(DOWN * 2.8)
        self.play(Write(note), Write(note2))
        self.wait(1.2)

        self.clear_scene()

    # ══════════════════════════════════════════════
    # 5. PARSE MULTI-RANGE — INTI TRANSFORMASI
    # ══════════════════════════════════════════════
    def parse_multi_range(self):
        title = Text("Parse Multi-Range Kriteria", font_size=32, color=YELLOW)
        title.to_edge(UP, buff=0.4)
        self.play(Write(title))

        explanation = Text(
            "Mengubah string kriteria → list kondisi numerik",
            font_size=20,
            color=GRAY_C,
        ).next_to(title, DOWN, buff=0.25)
        self.play(Write(explanation))

        # ── Kiri: tabel contoh parsing ──
        examples = [
            ('"6.0-7.0"', "[{min: 6.0, max: 7.0}]", C_S1),
            ('"5.0-6.0"', "[{min: 5.0, max: 6.0}]", C_S2),
            ('"<4.0, >9.0"', "[{max: 4.0, max_inclusive: False},\n{min: 9.0, min_inclusive: False}]", C_N),
            ('">2.0"', "[{min: 2.0, min_inclusive: False}]", C_S1),
            ('"1.5-2.0"', "[{min: 1.5, max: 2.0}]", C_S2),
            ('"1.0-1.5"', "[{min: 1.0, max: 1.5}]", C_S3),
            ('"<1.0"', "[{max: 1.0, max_inclusive: False}]", C_N),
            ('"sedang"', "[text_match: 'sedang']", C_S1),
        ]
        parse_data = [["String", "Hasil Parse"]] + [[raw, parsed] for raw, parsed, _ in examples]
        parse_table = make_table(parse_data, [YELLOW, YELLOW], font_size=16, pad_x=0.2, pad_y=0.07)
        for row, (_, _, color) in zip(parse_table[1:], examples):
            row[1].set_color(color)
            row[2].set_color(color)

        # ── Kanan: langkah fungsi ──
        code_title = VGroup(
            Text("Fungsi:", font_size=18, color=YELLOW, weight=BOLD),
            Text("_parse_multi_range(value_str) → list[dict]", font_size=18, color=YELLOW),
        ).arrange(DOWN, buff=0.08, aligned_edge=LEFT)
        code_lines = [
            "1. Split by koma → OR condition",
            '2. Deteksi "<" → max_inclusive=False',
            '3. Deteksi ">" → min_inclusive=False',
            '4. Deteksi "-" → range min-max',
            "5. Nilai tunggal → min = max",
            '6. "-" atau "" → [] (no criteria)',
        ]
        code_group = VGroup(
            *[Text(line, font_size=18, color=GRAY_C) for line in code_lines]
        ).arrange(DOWN, buff=0.15, aligned_edge=LEFT)
        code_panel = boxed(
            VGroup(code_title, code_group).arrange(DOWN, buff=0.25, aligned_edge=LEFT),
            YELLOW,
            buff=0.3,
        )

        layout = VGroup(parse_table, code_panel).arrange(RIGHT, buff=0.5)
        fit(layout, max_w=SAFE_W, max_h=4.6)
        layout.move_to(DOWN * 0.7)

        self.play(
            LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in parse_table], lag_ratio=0.15),
            run_time=2.2,
        )
        self.wait(1)
        self.play(FadeIn(code_panel), run_time=0.8)
        self.wait(2)

        self.clear_scene()

    # ══════════════════════════════════════════════
    # 6. TRANSFORMASI NILAI — DATA ASLI APLIKASI
    # ══════════════════════════════════════════════
    def value_transformation(self):
        title = Text("Transformasi Nilai Atribut", font_size=32, color=YELLOW)
        title.to_edge(UP, buff=0.4)
        self.play(Write(title))

        raw_data = [
            ["Field", "Nilai", "Parameter"],
            ["PH_NILAI", "6.0", "pH Tanah"],
            ["CORG_NILAI", "1.52", "C-Organik (%)"],
            ["KTK_NILAI", "21.05", "KTK (me/100g)"],
            ["TEKSTUR", "sandy loam", "Tekstur"],
            ["DALAM_TNH", "0 - 110", "Kedalaman (cm)"],
            ["KL", ">45%", "Kemiringan (%)"],
        ]
        criteria_data = [
            ["Parameter", "Kondisi (setelah parse)"],
            ["pH Tanah", "6.0 ≤ val ≤ 7.0"],
            ["C-Organik", "val > 2.0"],
            ["KTK", "17.0 ≤ val ≤ 25.0"],
            ["Tekstur", "text == 'sedang'"],
            ["Kedalaman", "val > 60"],
            ["Kemiringan", "val > 15%"],
        ]

        raw_table = make_table(raw_data, [BLUE, BLUE, GRAY_C], font_size=20)
        crit_table = make_table(criteria_data, [BLUE, YELLOW], font_size=20)
        mid = arrow_with_label("Cocokkan", YELLOW, 1.2)

        tables = VGroup(raw_table, mid, crit_table).arrange(RIGHT, buff=0.3)
        fit(tables, max_w=SAFE_W, max_h=3.3)
        tables.move_to(UP * 0.6)

        raw_label = Text("Data Shapefile", font_size=16, color=BLUE)
        raw_label.next_to(raw_table, UP, buff=0.15)
        crit_label = Text("Kriteria Ter-Parse", font_size=16, color=YELLOW)
        crit_label.next_to(crit_table, UP, buff=0.15)

        self.play(FadeIn(raw_label), FadeIn(raw_table, shift=RIGHT * 0.3), run_time=0.8)
        self.reveal_arrow(mid)
        self.play(FadeIn(crit_label), FadeIn(crit_table, shift=LEFT * 0.3), run_time=0.8)
        self.wait(0.5)

        transform_title = Text("Proses Transformasi", font_size=18, color=YELLOW)
        transform_title.to_edge(DOWN, buff=0.35)
        self.play(Write(transform_title))

        rows_data = [
            (1, "6.0", "6.0 ≤ 6.0 ≤ 7.0 → cocok S1", "S1", C_S1),
            (2, "1.52", "1.52 > 2.0? tidak → cek S2: 1.5 ≤ 1.52 ≤ 2.0 → cocok S2", "S2", C_S2),
            (3, "21.05", "21.05 > 25.0? tidak → cek S2: 17 ≤ 21.05 ≤ 25 → cocok S2", "S2", C_S2),
            (4, "sandy loam", "sandy loam == 'sedang' → cocok S1", "S1", C_S1),
            (5, "110 cm", "110 > 60 → cocok S1", "S1", C_S1),
            (6, "45%", "45 > 15 → cocok N (kelas terburuk)", "N", C_N),
        ]

        for row_idx, raw_val, match_detail, result_class, result_color in rows_data:
            raw_hl = highlight_row(raw_table, row_idx, YELLOW)
            crit_hl = highlight_row(crit_table, row_idx, YELLOW)
            self.play(FadeIn(raw_hl), FadeIn(crit_hl), run_time=0.3)

            # Detail + hasil dalam satu baris, ditengahkan di bawah tabel
            detail = Text(match_detail, font_size=18, color=result_color)
            chip = make_result_chip(raw_val, result_class, result_color)
            result_line = VGroup(detail, chip).arrange(RIGHT, buff=0.4)
            fit(result_line, max_w=SAFE_W)
            result_line.move_to(DOWN * 2.4)

            self.play(FadeIn(result_line, shift=UP * 0.2), run_time=0.5)
            self.wait(0.5)
            self.play(FadeOut(raw_hl), FadeOut(crit_hl), FadeOut(result_line), run_time=0.2)

        self.wait(0.8)

        summary = Text(
            "Setiap nilai dicocokkan dengan kondisi hasil parse → dapat skor S1/S2/S3/N",
            font_size=20,
            color=YELLOW,
        ).to_edge(DOWN, buff=0.35)
        fit(summary, max_w=SAFE_W)
        self.play(ReplacementTransform(transform_title, summary), run_time=0.8)
        self.wait(1.2)

        self.clear_scene()

    # ══════════════════════════════════════════════
    # 7. SKORING & KLASIFIKASI — METODE FAKTOR PEMBATAS
    # ══════════════════════════════════════════════
    def scoring_classification(self):
        title = Text("Skoring & Klasifikasi Akhir", font_size=32, color=ORANGE)
        title.to_edge(UP, buff=0.4)
        self.play(Write(title))

        # ── Tabel skor ──
        score_data = [
            ["Parameter", "Nilai", "Skor"],
            ["pH Tanah", "6.0", "S1"],
            ["C-Organik", "1.52%", "S2"],
            ["KTK", "21.05", "S2"],
            ["Tekstur", "sandy loam", "S1"],
            ["Kedalaman", "110 cm", "S1"],
            ["Kemiringan", "45%", "N"],
        ]
        score_table = make_table(score_data, [BLUE, GRAY_C, WHITE], font_size=20)
        color_scores(score_table)
        fit(score_table, max_w=5.0, max_h=3.1)

        # ── Panah + kotak metode ──
        arrow_grp = arrow_with_label("Metode Faktor\nPembatas", ORANGE, 1.4, font_size=18)

        heading = Text(
            "Metode Faktor Pembatas (Minimum Method)",
            font_size=18,
            color=ORANGE,
            weight=BOLD,
        )
        formula = make_formula(26, WHITE)
        desc = VGroup(
            Text("Kelas akhir ditentukan berdasarkan", font_size=18, color=ORANGE),
            Text("kelas terendah yang diperoleh.", font_size=18, color=ORANGE),
            Text("Semua S1 → kelas akhir S1", font_size=18, color=C_S1),
            Text("Ada karakteristik N → kelas akhir N", font_size=18, color=C_N),
        ).arrange(DOWN, buff=0.12, aligned_edge=LEFT)
        method_content = VGroup(heading, formula, desc).arrange(DOWN, buff=0.3)
        method = boxed(method_content, ORANGE, buff=0.3)

        layout = VGroup(score_table, arrow_grp, method).arrange(RIGHT, buff=0.4)
        fit(layout, max_w=SAFE_W)
        layout.move_to(UP * 0.8)

        score_label = Text("Skor per Parameter", font_size=18, color=GREEN)
        score_label.next_to(score_table, UP, buff=0.15)

        self.play(FadeIn(score_label), FadeIn(score_table, shift=RIGHT * 0.3))
        self.reveal_arrow(arrow_grp)
        self.play(FadeIn(method))
        self.wait(1.5)

        # ── Iterasi prioritas: dari kelas terburuk ──
        priorities = ["Unknown", "N", "S3", "S2", "S1"]
        prio_title = Text("Iterasi dari kelas terburuk:", font_size=20, color=ORANGE)
        prio_texts, parts = [], []
        for i, p in enumerate(priorities):
            t = Text(p, font_size=22, color=CLASS_COLORS[p])
            prio_texts.append(t)
            parts.append(t)
            if i < len(priorities) - 1:
                parts.append(Text(">", font_size=22, color=GRAY_C))
        prio_row = VGroup(*parts).arrange(RIGHT, buff=0.2)
        prio_line = VGroup(prio_title, prio_row).arrange(RIGHT, buff=0.4).move_to(DOWN * 1.55)
        self.play(FadeIn(prio_line))

        for i, p in enumerate(priorities):
            hl = SurroundingRectangle(prio_texts[i], color=ORANGE, buff=0.08, stroke_width=2)
            self.play(Create(hl), run_time=0.3)

            if p == "N":
                score_hl = highlight_row(score_table, 6, C_N)
                self.play(FadeIn(score_hl), run_time=0.3)
                found = Text(
                    "N ditemukan pada Kemiringan Lereng → berhenti",
                    font_size=20,
                    color=C_N,
                ).move_to(DOWN * 2.15)
                self.play(Write(found))
                self.wait(0.5)
                break
            else:
                self.play(FadeOut(hl), run_time=0.15)

        # ── Hasil akhir ──
        result_title = Text("Hasil Klasifikasi:", font_size=22, color=GREEN)
        result = Text("N — Tidak Sesuai", font_size=34, color=C_N, weight=BOLD)
        result_line = VGroup(result_title, result).arrange(RIGHT, buff=0.5).move_to(DOWN * 3.1)
        frame = SurroundingRectangle(result, color=C_N, buff=0.15, stroke_width=3)

        self.play(Write(result_title))
        self.play(FadeIn(result, scale=0.5), run_time=0.8)
        self.play(Create(frame))
        self.wait(2)

        self.clear_scene()

    # ══════════════════════════════════════════════
    # 8. STATISTIK HASIL — BAR CHART
    # ══════════════════════════════════════════════
    def final_result(self):
        title = Text("Statistik Kesesuaian Lahan", font_size=32, color=GREEN)
        title.to_edge(UP, buff=0.4)
        self.play(Write(title))

        bar_data = [
            ("S1", "Sangat Sesuai", 25),
            ("S2", "Cukup Sesuai", 40),
            ("S3", "Sesuai Marginal", 20),
            ("N", "Tidak Sesuai", 15),
        ]

        chart_title = Text("Distribusi Kesesuaian Lahan (%)", font_size=20, color=GRAY_C)
        chart_title.move_to(UP * 2.6)

        base_y = -2.0
        spacing = 2.6
        baseline = Line(
            [-5.2, base_y, 0], [5.2, base_y, 0], color=GRAY_C, stroke_width=2
        )

        bars, pcts, names = VGroup(), VGroup(), VGroup()
        for i, (cls, desc, val) in enumerate(bar_data):
            x = (i - 1.5) * spacing
            color = CLASS_COLORS[cls]

            bar = Rectangle(width=1.2, height=val * 0.08)
            bar.set_fill(color, 0.9).set_stroke(color, 1)
            bar.move_to([x, base_y, 0], aligned_edge=DOWN)  # semua batang berdiri di alas yang sama
            bars.add(bar)

            pcts.add(Text(f"{val}%", font_size=24, color=color, weight=BOLD).next_to(bar, UP, buff=0.12))

            label = VGroup(
                Text(cls, font_size=24, color=color, weight=BOLD),
                Text(desc, font_size=16, color=GRAY_C),
            ).arrange(DOWN, buff=0.06)
            label.move_to([x, base_y - 0.55, 0])
            names.add(label)

        self.play(FadeIn(chart_title), Create(baseline), run_time=0.6)
        self.play(*[GrowFromEdge(b, DOWN) for b in bars], run_time=1.4)
        self.play(FadeIn(pcts), FadeIn(names), run_time=0.6)
        self.wait(2.5)

        self.clear_scene()

    # ══════════════════════════════════════════════
    # MAIN
    # ══════════════════════════════════════════════
    def construct(self):
        self.title_slide()
        self.pipeline_overview()
        self.upload_zip()
        self.load_criteria()
        self.parse_multi_range()
        self.value_transformation()
        self.scoring_classification()
        self.final_result()

        # Closing
        closing = Text("Terima Kasih", font_size=44, color=BLUE, weight=BOLD)
        self.play(Write(closing), run_time=1)
        self.wait(2)
        self.play(FadeOut(closing))