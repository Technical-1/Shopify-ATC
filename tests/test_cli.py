import pytest

import shopify_atc.cli as cli
from shopify_atc.cli import build_parser, main
from shopify_atc.client import Product, Variant, NetworkError

PRODUCTS = [
    Product(
        title="Cool Shirt",
        handle="cool-shirt",
        variants=[
            Variant(id=111, title="Small", available=True, price="20.00"),
            Variant(id=222, title="Large", available=False, price="20.00"),
        ],
    )
]


def test_main_success_prints_output(monkeypatch, capsys):
    monkeypatch.setattr(cli, "fetch_products", lambda *a, **k: PRODUCTS)
    rc = main(["https://shop.example"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "Cool Shirt" in out
    assert "id=111" in out


def test_main_in_stock_only_filters(monkeypatch, capsys):
    monkeypatch.setattr(cli, "fetch_products", lambda *a, **k: PRODUCTS)
    rc = main(["https://shop.example", "--in-stock-only"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "id=111" in out
    assert "id=222" not in out


def test_main_maps_error_to_exit_code(monkeypatch, capsys):
    def boom(*a, **k):
        raise NetworkError("nope")

    monkeypatch.setattr(cli, "fetch_products", boom)
    rc = main(["https://shop.example"])
    assert rc == 2  # NetworkError.exit_code
    assert "nope" in capsys.readouterr().err


def test_build_parser_defaults():
    args = build_parser().parse_args(["https://shop.example"])
    assert args.store_url == "https://shop.example"
    assert args.limit == 250
    assert args.quantity == 1
    assert args.format == "text"
    assert args.in_stock_only is False


def test_main_rejects_non_positive_limit():
    with pytest.raises(SystemExit) as exc:
        main(["https://shop.example", "--limit", "0"])
    assert exc.value.code == 2  # argparse usage error


def _sample():
    return [Product(title="Tee", handle="tee", variants=[Variant(id=111, title="S", available=True, price="20.00")])]


def test_main_quantity_flows_into_cart_links(monkeypatch, capsys):
    monkeypatch.setattr(cli, "fetch_products", lambda *a, **k: _sample())
    exit_code = cli.main(["https://example.com", "--quantity", "3"])
    out = capsys.readouterr().out
    assert exit_code == 0
    assert "quantity=3" in out


def test_main_format_json_emits_json(monkeypatch, capsys):
    import json

    monkeypatch.setattr(cli, "fetch_products", lambda *a, **k: _sample())
    exit_code = cli.main(["https://example.com", "--format", "json"])
    out = capsys.readouterr().out
    assert exit_code == 0
    data = json.loads(out)
    assert data[0]["handle"] == "tee"
    assert data[0]["variants"][0]["add_url"].endswith("quantity=1")


def test_main_format_csv_emits_header(monkeypatch, capsys):
    monkeypatch.setattr(cli, "fetch_products", lambda *a, **k: _sample())
    exit_code = cli.main(["https://example.com", "--format", "csv"])
    out = capsys.readouterr().out
    assert exit_code == 0
    assert out.splitlines()[0] == "product_title,variant_title,price,available,add_url"


def test_main_version_exits_zero(capsys):
    import shopify_atc

    with pytest.raises(SystemExit) as excinfo:
        cli.main(["--version"])
    assert excinfo.value.code == 0
    out = capsys.readouterr().out
    assert shopify_atc.__version__ in out
