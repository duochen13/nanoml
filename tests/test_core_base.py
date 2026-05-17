from nanoml.core.base import Component, Provider


def test_component_base_class():
    """Component base class should be instantiable."""

    class TestComponent(Component):
        def run(self):
            return "component executed"

    component = TestComponent(name="test")
    assert component.name == "test"
    assert component.run() == "component executed"


def test_provider_base_class():
    """Provider base class should be instantiable."""

    class TestProvider(Provider):
        def deploy(self):
            return "deployed"

    provider = TestProvider(environment="local")
    assert provider.environment == "local"
    assert provider.deploy() == "deployed"
