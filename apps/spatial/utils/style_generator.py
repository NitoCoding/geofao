"""
Style Generator Utility

Modul ini untuk generate SLD (Styled Layer Descriptor) otomatis berdasarkan
kategori layer dan tipe geometri.
"""

import logging

logger = logging.getLogger(__name__)

# Color palette berdasarkan kategori layer
COLOR_PALETTE = {
    'tanah': '#8B4513',      # Brown untuk karakteristik tanah
    'komoditas': '#228B22',  # Green untuk komoditas pertanian
    'lainnya': '#4169E1',    # Blue untuk default
}

# Default color jika layer tidak punya kategori
DEFAULT_COLOR = '#4169E1'


def get_color_for_category(category):
    """
    Mendapatkan warna berdasarkan kategori layer.

    Args:
        category: Kategori layer ('tanah', 'komoditas', 'lainnya')

    Returns:
        str: Hex color code
    """
    return COLOR_PALETTE.get(category, DEFAULT_COLOR)


def generate_default_sld(layer):
    """
    Generate default SLD berdasarkan tipe layer dan kategori.

    Args:
        layer: MasterLayer instance

    Returns:
        str: SLD XML content

    Examples:
        >>> layer.layer_type = 'polygon'
        >>> layer.layer_category = 'tanah'
        >>> generate_default_sld(layer)
        '<?xml version="1.0" encoding="UTF-8"?><StyledLayerDescriptor...'
    """
    try:
        layer_name = layer.name
        layer_type = layer.layer_type
        category = layer.layer_category if layer.layer_category else 'lainnya'

        # Tentukan warna berdasarkan kategori
        fill_color = get_color_for_category(category)

        logger.info(f"Generating SLD for layer '{layer_name}' (type: {layer_type}, category: {category})")

        # Generate SLD berdasarkan tipe geometri
        if layer_type == 'polygon':
            return generate_polygon_sld(layer_name, fill_color)
        elif layer_type == 'linestring':
            return generate_linestring_sld(layer_name, fill_color)
        elif layer_type == 'point':
            return generate_point_sld(layer_name, fill_color)
        elif layer_type == 'multipolygon':
            return generate_polygon_sld(layer_name, fill_color)
        else:
            logger.warning(f"Unknown layer type '{layer_type}', using generic SLD")
            return generate_generic_sld(layer_name, fill_color)

    except Exception as e:
        logger.error(f"Error generating default SLD: {e}")
        # Return generic SLD as fallback
        return generate_generic_sld(layer.name if hasattr(layer, 'name') else 'layer', DEFAULT_COLOR)


def generate_polygon_sld(layer_name, fill_color):
    """
    Generate SLD untuk polygon/multipolygon.

    Args:
        layer_name: Nama layer
        fill_color: Warna fill (hex code)

    Returns:
        str: SLD XML string
    """
    sld = f"""<?xml version="1.0" encoding="UTF-8"?>
<StyledLayerDescriptor version="1.0.0"
    xsi:schemaLocation="http://www.opengis.net/sld StyledLayerDescriptor.xsd"
    xmlns="http://www.opengis.net/sld"
    xmlns:ogc="http://www.opengis.net/ogc"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <NamedLayer>
    <Name>{layer_name}</Name>
    <UserStyle>
      <Title>{layer_name} Style</Title>
      <FeatureTypeStyle>
        <Rule>
          <PolygonSymbolizer>
            <Fill>
              <CssParameter name="fill">{fill_color}</CssParameter>
              <CssParameter name="fill-opacity">0.6</CssParameter>
            </Fill>
            <Stroke>
              <CssParameter name="stroke">#000000</CssParameter>
              <CssParameter name="stroke-width">1</CssParameter>
              <CssParameter name="stroke-opacity">1</CssParameter>
            </Stroke>
          </PolygonSymbolizer>
        </Rule>
      </FeatureTypeStyle>
    </UserStyle>
  </NamedLayer>
</StyledLayerDescriptor>"""
    return sld


def generate_linestring_sld(layer_name, stroke_color):
    """
    Generate SLD untuk linestring.

    Args:
        layer_name: Nama layer
        stroke_color: Warna stroke (hex code)

    Returns:
        str: SLD XML string
    """
    sld = f"""<?xml version="1.0" encoding="UTF-8"?>
<StyledLayerDescriptor version="1.0.0"
    xsi:schemaLocation="http://www.opengis.net/sld StyledLayerDescriptor.xsd"
    xmlns="http://www.opengis.net/sld"
    xmlns:ogc="http://www.opengis.net/ogc"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <NamedLayer>
    <Name>{layer_name}</Name>
    <UserStyle>
      <Title>{layer_name} Style</Title>
      <FeatureTypeStyle>
        <Rule>
          <LineSymbolizer>
            <Stroke>
              <CssParameter name="stroke">{stroke_color}</CssParameter>
              <CssParameter name="stroke-width">2</CssParameter>
              <CssParameter name="stroke-linecap">round</CssParameter>
              <CssParameter name="stroke-linejoin">round</CssParameter>
              <CssParameter name="stroke-opacity">1</CssParameter>
            </Stroke>
          </LineSymbolizer>
        </Rule>
      </FeatureTypeStyle>
    </UserStyle>
  </NamedLayer>
</StyledLayerDescriptor>"""
    return sld


def generate_point_sld(layer_name, fill_color):
    """
    Generate SLD untuk point.

    Args:
        layer_name: Nama layer
        fill_color: Warna fill (hex code)

    Returns:
        str: SLD XML string
    """
    sld = f"""<?xml version="1.0" encoding="UTF-8"?>
<StyledLayerDescriptor version="1.0.0"
    xsi:schemaLocation="http://www.opengis.net/sld StyledLayerDescriptor.xsd"
    xmlns="http://www.opengis.net/sld"
    xmlns:ogc="http://www.opengis.net/ogc"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <NamedLayer>
    <Name>{layer_name}</Name>
    <UserStyle>
      <Title>{layer_name} Style</Title>
      <FeatureTypeStyle>
        <Rule>
          <PointSymbolizer>
            <Graphic>
              <Mark>
                <WellKnownName>circle</WellKnownName>
                <Fill>
                  <CssParameter name="fill">{fill_color}</CssParameter>
                  <CssParameter name="fill-opacity">1</CssParameter>
                </Fill>
                <Stroke>
                  <CssParameter name="stroke">#000000</CssParameter>
                  <CssParameter name="stroke-width">1</CssParameter>
                  <CssParameter name="stroke-opacity">1</CssParameter>
                </Stroke>
              </Mark>
              <Size>10</Size>
            </Graphic>
          </PointSymbolizer>
        </Rule>
      </FeatureTypeStyle>
    </UserStyle>
  </NamedLayer>
</StyledLayerDescriptor>"""
    return sld


def generate_generic_sld(layer_name, color):
    """
    Generate generic SLD (fallback untuk tipe tidak dikenal).

    Args:
        layer_name: Nama layer
        color: Warna (hex code)

    Returns:
        str: SLD XML string
    """
    sld = f"""<?xml version="1.0" encoding="UTF-8"?>
<StyledLayerDescriptor version="1.0.0"
    xsi:schemaLocation="http://www.opengis.net/sld StyledLayerDescriptor.xsd"
    xmlns="http://www.opengis.net/sld"
    xmlns:ogc="http://www.opengis.net/ogc"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <NamedLayer>
    <Name>{layer_name}</Name>
    <UserStyle>
      <Title>{layer_name} Style</Title>
      <FeatureTypeStyle>
        <Rule>
          <PolygonSymbolizer>
            <Fill>
              <CssParameter name="fill">{color}</CssParameter>
              <CssParameter name="fill-opacity">0.6</CssParameter>
            </Fill>
            <Stroke>
              <CssParameter name="stroke">#000000</CssParameter>
              <CssParameter name="stroke-width">1</CssParameter>
            </Stroke>
          </PolygonSymbolizer>
        </Rule>
      </FeatureTypeStyle>
    </UserStyle>
  </NamedLayer>
</StyledLayerDescriptor>"""
    return sld
