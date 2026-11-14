import pytest
from io import BytesIO
import h5py

from tanksim.physics import TankPhysicalProperty, LinkPhysicalProperty
from tanksim.postprocessing import ReadResults
from tanksim.postprocessing.time_evolution import TimeEvolution
from tanksim.postprocessing.read_results import _get_element_name, _get_element_reader
from tanksim.postprocessing.reader import TankReader, LinkReader
from tanksim.tank import Tank, Geometry, Port
from tanksim.models import Orifice
from tanksim.boundaries import Atmosphere
from tanksim.link import Link


@pytest.mark.parametrize("element_name, property", [("TANK-A", TankPhysicalProperty.MASS),
                                                    ("connection", LinkPhysicalProperty.MASSFLOW)])
def test_save_pdf_exports_requested_evolution(tmp_path, element_name, property):
    results = ReadResults(tmp_path / "results.h5")

    evolution = TimeEvolution(
        time=[0.0, 1.0],
        value=[10.0, 8.0],
    )

    results.add_requested_variable(element_name, property, evolution)

    output = results.save_pdf()

    assert output == tmp_path / "results.pdf"
    assert output.is_file()
    assert output.read_bytes().startswith(b"%PDF-")


def make_link(name):
    tank = Tank("SOURCE")
    tank.set_geometry(Geometry(height=1.0, surface=1.0))

    return Link(
        name=name,
        upstream=Port(tank, 0.0),
        downstream=Atmosphere(),
        model=Orifice(diameter=0.1),
    )


@pytest.mark.parametrize(
        "factory, name", 
        [
            (Tank, "TANK"),
            (make_link, "LINK"),
            (str, "ELEMENT_NAME"),
        ])
def test_get_element_name(factory, name):
    elem = factory(name)

    assert _get_element_name(elem) == name


class DummyElement():
    pass

def test_get_element_name_rejects_unsupported_type():
    with pytest.raises(TypeError, match="Unsupported type: DummyElement"):
        _get_element_name(DummyElement())


@pytest.mark.parametrize(
    "factory, name, class_name, expected_reader",
    [
        (Tank, "TANK", "Tank", TankReader),
        (make_link, "LINK", "Link", LinkReader),
        (str, "TANK", "Tank", TankReader),
        (str, "LINK", "Link", LinkReader),
    ],
)
def test_get_element_reader(factory, name, class_name, expected_reader):
    element = factory(name)

    with h5py.File(BytesIO(), "w") as file:
        group = file.create_group(f"{name}/type")
        group.attrs["class_name"] = class_name

        reader = _get_element_reader(file, element)

        assert isinstance(reader, expected_reader)


def test_get_element_reader_rejects_unsupported_type():
    with h5py.File(BytesIO(), "w") as file:
        with pytest.raises(TypeError, match="Unsupported type: DummyElement"):
            _get_element_reader(file, DummyElement())


def test_get_element_reader_str_not_found():
    with h5py.File(BytesIO(), "w") as file:
        with pytest.raises(KeyError, match="Requested element name 'Link' not found."):
            _get_element_reader(file, "Link")


def test_get_element_reader_str_found_but_unsupported():
    dummy = DummyElement()

    with h5py.File(BytesIO(), "w") as file:
        group = file.create_group(f"dummy/type")
        group.attrs["class_name"] = type(dummy).__name__

        with pytest.raises(TypeError, match="Unsupported stored class: 'DummyElement'"):
            _get_element_reader(file, "dummy")

def test_generate_csv_report():
    dummy = DummyElement()

    with h5py.File(BytesIO(), "w") as file:
        group = file.create_group(f"dummy/type")
        group.attrs["class_name"] = type(dummy).__name__

        with pytest.raises(TypeError, match="Unsupported stored class: 'DummyElement'"):
            _get_element_reader(file, "dummy")

def test_generate_report_writes_expected_values(tmp_path):
    results = ReadResults(tmp_path / "results.h5")

    results.add_requested_variable(
        "TANK",
        TankPhysicalProperty.MASS,
        TimeEvolution(time=[0.0, 1.0], value=[1000.0, 800.0]),
    )
    results.add_requested_variable(
        "TANK",
        TankPhysicalProperty.LEVEL,
        TimeEvolution(time=[0.0, 1.0], value=[1.0, 0.8]),
    )

    path = tmp_path / "report.txt"
    results.generate_report(path)

    assert path.is_file()

    lines = path.read_text().splitlines()

    assert lines[0].split() == [
        "time",
        "TANK_liquid_mass",
        "TANK_level",
    ]

    # split() ignore les espaces utilisés pour aligner le tableau.
    rows = [
        [float(value) for value in line.split()]
        for line in lines[1:]
    ]

    assert len(rows) == 2
    assert rows[0] == pytest.approx([0.0, 1000.0, 1.0])
    assert rows[1] == pytest.approx([1.0, 800.0, 0.8])


def test_generate_report_rejects_empty_selection(tmp_path):
    results = ReadResults(tmp_path / "results.h5")

    with pytest.raises(ValueError, match="No requested variables"):
        results.generate_report(tmp_path / "report.txt")


def test_generate_report_rejects_different_time_samples(tmp_path):
    results = ReadResults(tmp_path / "results.h5")

    results.add_requested_variable(
        "TANK",
        TankPhysicalProperty.MASS,
        TimeEvolution(time=[0.0, 1.0], value=[1000.0, 800.0]),
    )
    results.add_requested_variable(
        "TANK",
        TankPhysicalProperty.LEVEL,
        TimeEvolution(time=[0.0, 2.0], value=[1.0, 0.8]),
    )

    with pytest.raises(ValueError, match="Time samples differ"):
        results.generate_report(tmp_path / "report.txt")