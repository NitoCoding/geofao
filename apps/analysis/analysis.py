"""
Land Suitability Analysis Module

Modul ini untuk menganalisis kesesuaian lahan menggunakan FAO Minimum Method.

FAO Minimum Method adalah standar internasional untuk evaluasi kesesuaian lahan
di mana kelas kesesuaian overall ditentukan oleh kelas terendah (terburuk)
dari semua karakteristik lahan yang dianalisis.

Classes:
    - S1: Sangat Sesuai (Highly Suitable)
    - S2: Cukup Sesuai (Moderately Suitable)
    - S3: Sesuai Marginal (Marginally Suitable)
    - N: Tidak Sesuai (Not Suitable)
"""

from typing import Any, Optional
from collections import Counter
from django.utils import timezone
import logging
import re

from apps.master_data.models import (
    Commodity,
    SuitabilityCharacteristic,
)

logger = logging.getLogger(__name__)


def recommend_crops_for_land(
    soil_data: dict[str, Any],
    limit: int = None,
) -> list[dict]:
    """
    Rekomendasikan komoditas yang sesuai untuk suatu unit lahan.

    Fungsi ini menjalankan analisis kesesuaian lahan untuk seluruh komoditas
    yang terdaftar dan mengembalikan komoditas yang memperoleh kelas S1
    (Sangat Sesuai) atau S2 (Cukup Sesuai).

    Pendekatan ini menggunakan prinsip 'reverse matching': daripada mencari
    lahan yang cocok untuk tanaman tertentu, sistem menemukan tanaman yang
    cocok untuk lahan tertentu berdasarkan data karakteristik lahan yang
    diinput.

    Args:
        soil_data: Dictionary data tanah {characteristic_name: value}
        limit: Batas maksimum jumlah rekomendasi (None = tanpa batas)

    Returns:
        List rekomendasi komoditas yang sesuai (S1 atau S2), diurutkan
        dari yang paling sesuai (S1) ke S2. Setiap item berisi:
        {
            'commodity_id': int,
            'commodity_name': str,
            'group_name': str,
            'overall_class': str,
            'overall_class_display': str,
            'overall_score': float,
        }
    """
    if not soil_data:
        raise ValueError("soil_data cannot be empty")

    recommendations = []

    commodities = Commodity.objects.select_related('group').all()

    for commodity in commodities:
        try:
            result = analyze_suitability(
                commodity.id,
                soil_data,
            )

            # Hanya ambil yang S1 atau S2
            if result['overall_class'] in ['S1', 'S2']:
                recommendations.append({
                    'commodity_id': commodity.id,
                    'commodity_name': commodity.name,
                    'group_name': commodity.group.name if commodity.group else '',
                    'overall_class': result['overall_class'],
                    'overall_class_display': result['overall_class_display'],
                    'overall_score': result['overall_score'],
                })

        except Exception as e:
            logger.warning(
                f"Analysis failed for commodity '{commodity.name}': {e}"
            )

    # Sort: S1 di atas, S2 di bawah; dalam grup yang sama, skor lebih tinggi dulu
    recommendations.sort(
        key=lambda x: (
            0 if x['overall_class'] == 'S1' else 1,
            -x['overall_score']
        )
    )

    if limit:
        recommendations = recommendations[:limit]

    return recommendations


# Constants
SUITABILITY_SCORES = {
    'S1': 4,
    'S2': 3,
    'S3': 2,
    'N': 1,
    'Unknown': 0
}

SUITABILITY_CLASS_DISPLAYS = {
    'S1': 'Sangat Sesuai',
    'S2': 'Cukup Sesuai',
    'S3': 'Sesuai Marginal',
    'N': 'Tidak Sesuai',
    'Unknown': 'Tidak Diketahui'
}

# FAO Minimum Method Priority: dari terburuk ke terbaik
MINIMUM_METHOD_PRIORITY = ['Unknown', 'N', 'S3', 'S2', 'S1']

CACHE_TIMEOUT = 3600  # 1 hour


def analyze_suitability(
    commodity_id: int,
    soil_data: dict[str, Any],
) -> dict[str, Any]:
    """
    Analisis kesesuaian lahan dengan FAO Minimum Method.

    Metode ini menggunakan standar FAO Framework di mana kelas kesesuaian
    overall ditentukan oleh kelas terendah (terburuk) dari semua karakteristik.

    Args:
        commodity_id: ID komoditas yang dianalisis
        soil_data: Dictionary data tanah {characteristic_name: value}

    Returns:
        Dictionary hasil analisis dengan struktur:
        {
            'commodity_id': int,
            'commodity_name': str,
            'overall_class': str,  # 'S1', 'S2', 'S3', or 'N'
            'overall_score': float,
            'characteristics': list[dict],
            'summary': dict
        }

    Example:
        >>> soil_data = {
        ...     'pH Tanah': 5.2,
        ...     'C-Organik': 1.8,
        ...     'Tekstur': 'Lempung'
        ... }
        >>> result = analyze_suitability(1, soil_data)
        >>> print(result['overall_class'])
        'S3'
    """
    # Validate commodity exists
    try:
        Commodity.objects.get(id=commodity_id)
    except Commodity.DoesNotExist:
        logger.error(f"Commodity with id {commodity_id} not found")
        raise ValueError(f"Commodity with id {commodity_id} not found")

    analyzer = SuitabilityAnalyzer(commodity_id)
    return analyzer.analyze(soil_data)


class SuitabilityAnalyzer:
    """
    Analyzer untuk kesesuaian lahan menggunakan FAO Minimum Method.

    Class ini menyederhanakan analisis kesesuaian lahan dengan hanya menggunakan
    metode minimum FAO, tanpa opsi metode weighted atau parametric.
    """

    MINIMUM_METHOD_PRIORITY = MINIMUM_METHOD_PRIORITY

    def __init__(self, commodity_id: int) -> None:
        """
        Initialize analyzer untuk komoditas tertentu.

        Args:
            commodity_id: ID komoditas yang akan dianalisis
        """
        self.commodity_id = commodity_id
        self.commodity = self._get_commodity()
        self.characteristics = self._get_characteristics()

        logger.info(
            "Initialized SuitabilityAnalyzer for commodity %s (%s) using FAO minimum method",
            commodity_id,
            self.commodity.name if self.commodity else 'Unknown'
        )

    def _get_commodity(self) -> Optional[Commodity]:
        """Get commodity object."""
        try:
            return Commodity.objects.get(id=self.commodity_id)
        except Commodity.DoesNotExist:
            logger.error(f"Commodity {self.commodity_id} not found")
            return None

    def _get_characteristics(self):
        """Get active characteristics for this commodity."""
        return SuitabilityCharacteristic.objects.filter(
            commodity_id=self.commodity_id,
            is_active=True
        )

    def analyze(
        self,
        soil_data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Analisis kesesuaian lahan berdasarkan data tanah.

        Args:
            soil_data: Dictionary data tanah

        Returns:
            Dictionary hasil analisis
        """
        if not soil_data:
            raise ValueError("soil_data cannot be empty")

        # Initialize counters
        characteristic_results = []
        class_counts = Counter({'S1': 0, 'S2': 0, 'S3': 0, 'N': 0, 'Unknown': 0})

        # Analyze each characteristic
        analyzed_count = 0
        skipped_count = 0
        for characteristic in self.characteristics:
            char_name = characteristic.name

            if char_name not in soil_data:
                if skipped_count == 0:
                    logger.warning(f"DEBUG: First skip — char_name='{char_name}', soil_data_keys={list(soil_data.keys())}")
                skipped_count += 1
                logger.debug(f"Characteristic {char_name} not found in soil_data")
                continue

            analyzed_count += 1
            current_value = soil_data[char_name]

            # Determine suitability class
            suitability_class = determine_suitability_class(
                current_value, characteristic
            )

            # Get score
            score = SUITABILITY_SCORES.get(suitability_class, 0)

            # Update counter
            class_counts[suitability_class] += 1

            # Build result — limiting_factor selalu None karena
            # data klasifikasi per karakteristik sudah disimpan
            # di SuitabilityAnalysisResultPerFeature.characteristic_results
            result = {
                'characteristic': char_name,
                'value': current_value,
                'suitability_class': suitability_class,
                'class_display': SUITABILITY_CLASS_DISPLAYS.get(
                    suitability_class, 'Tidak Diketahui'
                ),
                'score': score,
                'limiting_factor': None,
            }

            characteristic_results.append(result)

        # Calculate overall class using minimum method
        overall_class, overall_score = self._minimum_method(class_counts)

        # Build final result
        return {
            'commodity_id': self.commodity_id,
            'commodity_name': self.commodity.name if self.commodity else 'Unknown',
            'overall_class': overall_class,
            'overall_class_display': SUITABILITY_CLASS_DISPLAYS.get(
                overall_class, 'Tidak Diketahui'
            ),
            'overall_score': overall_score,
            'characteristics': characteristic_results,
            'summary': {
                'total_characteristics': len(characteristic_results),
                's1_count': class_counts['S1'],
                's2_count': class_counts['S2'],
                's3_count': class_counts['S3'],
                'n_count': class_counts['N'],
                'unknown_count': class_counts['Unknown'],
                'issues_count': class_counts['S3'] + class_counts['N'],
                'critical_count': class_counts['N']
            },
            'analyzed_at': timezone.now().isoformat()
        }

    def _minimum_method(self, class_counts: Counter) -> tuple[str, float]:
        """
        FAO Minimum Method: kelas overall = kelas terburuk.

        Args:
            class_counts: Counter dengan jumlah karakteristik per kelas

        Returns:
            Tuple (overall_class, overall_score)
        """
        for class_code in self.MINIMUM_METHOD_PRIORITY:
            if class_counts.get(class_code, 0) > 0:
                score = float(SUITABILITY_SCORES.get(class_code, 0))
                logger.debug(
                    f"Minimum method: class={class_code}, score={score}"
                )
                return class_code, score

        # Fallback jika tidak ada karakteristik yang dianalisis
        logger.warning("No characteristics analyzed, returning Unknown")
        return 'Unknown', 0.0


def determine_suitability_class(
    value: Any,
    characteristic: SuitabilityCharacteristic
) -> str:
    """
    Tentukan kelas kesesuaian berdasarkan nilai dan kriteria karakteristik.

    Args:
        value: Nilai dari data tanah (numeric atau text)
        characteristic: SuitabilityCharacteristic object

    Returns:
        Suitability class code: 'S1', 'S2', 'S3', or 'N'
    """
    if isinstance(value, str):
        numeric_value = _try_extract_numeric_from_string(value)
        if numeric_value is not None:
            result = _determine_class_for_numeric_value(numeric_value, characteristic)
            logger.info(
                f"  [{characteristic.name}] nilai='{value}' → numerik={numeric_value} → kelas={result}"
            )
            return result
        result = _determine_class_for_text_value(value, characteristic)
        logger.info(
            f"  [{characteristic.name}] nilai='{value}' → teks → kelas={result}"
        )
        return result

    # Handle numeric values
    try:
        numeric_value = float(value)
        result = _determine_class_for_numeric_value(numeric_value, characteristic)
        logger.info(
            f"  [{characteristic.name}] nilai={value} → numerik={numeric_value} → kelas={result}"
        )
        return result
    except (ValueError, TypeError):
        logger.warning(
            f"Could not convert value '{value}' to numeric for {characteristic.name}"
        )
        return 'Unknown'


def _determine_class_for_text_value(
    value: str,
    characteristic: SuitabilityCharacteristic
) -> str:
    """
    Determine class for text-based characteristics.

    Menggunakan field *_value (CharField) untuk pencocokan string.
    """
    value_lower = value.lower().strip()

    # Cek S1
    if characteristic.s1_value and value_lower == characteristic.s1_value.lower().strip():
        return 'S1'

    # Cek S2
    if characteristic.s2_value and value_lower == characteristic.s2_value.lower().strip():
        return 'S2'

    # Cek S3
    if characteristic.s3_value and value_lower == characteristic.s3_value.lower().strip():
        return 'S3'

    # Cek N
    if characteristic.n_value and value_lower == characteristic.n_value.lower().strip():
        return 'N'

    # Fallback: coba match di semua field *_value
    for class_code in ['s1', 's2', 's3', 'n']:
        field_value = getattr(characteristic, f'{class_code}_value', None)
        # Field bisa berisi beberapa nilai koma-separated, mis: "Lempung, Lempung Berpasir"
        if field_value:
            options = [opt.strip().lower() for opt in field_value.split(',')]
            if value_lower in options:
                return class_code.upper()

    logger.warning(f"No matching criteria for text value '{value}' in {characteristic.name}")
    return 'Unknown'


def _try_extract_numeric_from_string(value: str) -> Optional[float]:
    """
    Coba ekstrak nilai numerik dari string yang mungkin mengandung unit atau range.

    Contoh:
      "3-8%"     → 8.0 (ambil max, paling konservatif)
      ">45%"     → 45.0
      "0 - 110"  → 110.0
      "Lempung"  → None (benar-benar teks)

    Returns:
        Nilai float jika berhasil diekstrak, None jika benar-benar nilai teks.
    """
    cleaned = value.strip()

    cleaned = cleaned.rstrip('%')

    cleaned = re.sub(r'\s*–\s*|\s*-\s*', '-', cleaned)

    if cleaned.startswith('>='):
        try:
            return float(cleaned[2:])
        except ValueError:
            pass

    if cleaned.startswith('<='):
        try:
            return float(cleaned[2:])
        except ValueError:
            pass

    if cleaned.startswith('>'):
        try:
            return float(cleaned[1:])
        except ValueError:
            pass

    if cleaned.startswith('<'):
        try:
            return float(cleaned[1:])
        except ValueError:
            pass

    if '-' in cleaned:
        parts = cleaned.split('-', 1)
        try:
            vals = [float(p) for p in parts]
            return max(vals)
        except ValueError:
            pass

    try:
        return float(cleaned)
    except ValueError:
        logger.warning(f"Gagal ekstrak numerik dari '{value}' (cleaned='{cleaned}')")
        return None


def _parse_multi_range(value_str: str) -> list[dict]:
    """
    Parse kriteria range yang bisa berisi multi-kondisi (dipisah koma = OR).

    Format yang didukung:
      "1.500 – 2.000"              → [{min: 1500, max: 2000}]
      "1.000 – <1.500, >2.000 – 2.500" → [{min:1000, max:1500, max_inclusive:False}, ...]
      "<700, >3.000"               → [{max:700, max_inclusive:False}, {min:3000, min_inclusive:False}]
      "<=16"                       → [{max:16, max_inclusive:True}]
      ">=50"                       → [{min:50, min_inclusive:True}]
      "<4.0"                       → [{max:4.0, max_inclusive:False}]
      ">9.0"                       → [{min:9.0, min_inclusive:False}]
      "6.0"                        → [{min:6.0, max:6.0}]
      "-" atau ""                 → [] (tidak ada kriteria)

    Returns:
        List of condition dicts, masing-masing dengan:
        - min: float atau None
        - max: float atau None
        - min_inclusive: bool (default True)
        - max_inclusive: bool (default True)
    """
    value_str = value_str.strip()
    if not value_str or value_str == '-':
        return []

    conditions = []
    for part in value_str.split(','):
        part = part.strip()
        if not part or part == '-':
            continue

        part = re.sub(r'\s*–\s*', '-', part)

        cond = {'min': None, 'max': None, 'min_inclusive': True, 'max_inclusive': True}

        if '-' in part:
            left, right = part.split('-', 1)
            left, right = left.strip(), right.strip()

            if left.startswith('>='):
                cond['min'] = float(left[2:].strip())
                cond['min_inclusive'] = True
            elif left.startswith('<='):
                cond['max'] = float(left[2:].strip())
                cond['max_inclusive'] = True
            elif left.startswith('>'):
                cond['min'] = float(left[1:].strip())
                cond['min_inclusive'] = False
            elif left.startswith('<'):
                cond['max'] = float(left[1:].strip())
                cond['max_inclusive'] = False
            else:
                cond['min'] = float(left)

            if right.startswith('>='):
                cond['min'] = float(right[2:].strip())
                cond['min_inclusive'] = True
            elif right.startswith('<='):
                cond['max'] = float(right[2:].strip())
                cond['max_inclusive'] = True
            elif right.startswith('>'):
                cond['min'] = float(right[1:].strip())
                cond['min_inclusive'] = False
            elif right.startswith('<'):
                cond['max'] = float(right[1:].strip())
                cond['max_inclusive'] = False
            else:
                cond['max'] = float(right)
        elif part.startswith('<='):
            cond['max'] = float(part[2:].strip())
            cond['max_inclusive'] = True
        elif part.startswith('>='):
            cond['min'] = float(part[2:].strip())
            cond['min_inclusive'] = True
        elif part.startswith('<'):
            cond['max'] = float(part[1:].strip())
            cond['max_inclusive'] = False
        elif part.startswith('>'):
            cond['min'] = float(part[1:].strip())
            cond['min_inclusive'] = False
        else:
            val = float(part)
            cond['min'] = val
            cond['max'] = val

        conditions.append(cond)

    return conditions


def _determine_class_for_numeric_value(
    value: float,
    characteristic: SuitabilityCharacteristic
) -> str:
    """
    Determine class for numeric-based characteristics.

    Mendukung multi-kondisi dalam satu kelas (dipisah koma = OR).
    Format: "1.500 – 2.000", "<4.0, >8.5", "1.000 – <1.500", "-" (no criteria).
    """
    for class_code in ['s1', 's2', 's3', 'n']:
        value_str = getattr(characteristic, f'{class_code}_value', '')
        if not value_str:
            continue

        conditions = _parse_multi_range(value_str)
        if not conditions:
            continue

        for cond in conditions:
            if cond['min'] is not None:
                if cond['min_inclusive']:
                    if value < cond['min']:
                        continue
                else:
                    if value <= cond['min']:
                        continue
            if cond['max'] is not None:
                if cond['max_inclusive']:
                    if value > cond['max']:
                        continue
                else:
                    if value >= cond['max']:
                        continue
            return class_code.upper()

    logger.warning(
        f"No matching criteria for numeric value '{value}' in {characteristic.name} "
        f"(s1={characteristic.s1_value}, s2={characteristic.s2_value}, "
        f"s3={characteristic.s3_value}, n={characteristic.n_value})"
    )
    return 'Unknown'