"""AWS CDK app entry point."""
from aws_cdk import App, Environment
from stacks.networking_stack import NetworkingStack
from stacks.ml_stack import MLStack


def main():
    """Create and synthesize CDK app."""
    app = App()

    # Get environment from context
    env = Environment(
        account=app.node.try_get_context("account"),
        region=app.node.try_get_context("region") or "us-east-1"
    )

    # Create stacks
    networking = NetworkingStack(app, "NanoRec-Networking", env=env)
    ml = MLStack(app, "NanoRec-ML", vpc=networking.vpc, env=env)

    app.synth()


if __name__ == "__main__":
    main()
