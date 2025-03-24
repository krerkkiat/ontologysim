import os
import inspect
import sys
import argparse


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    serve_command_parser = subparsers.add_parser("serve", help="Run the development server.")
    serve_command_parser.add_argument("--bind", "-b", default="0.0.0.0")
    serve_command_parser.add_argument("--port", "-p", default=5000, type=int)

    ontology_command_parser = subparsers.add_parser("export-ontology", help="Export the simulation ontology to an RDF file.")
    ontology_command_parser.add_argument("outfile")

    help_command_parser = subparsers.add_parser("help", help="Show this help message.")

    args = parser.parse_args()

    if args.command == "serve":
        current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        parent_dir = os.path.dirname(current_dir)
        parent_parent_dir = os.path.dirname(parent_dir)
        sys.path.insert(0, parent_dir)
        sys.path.insert(0, parent_parent_dir)


        from ontologysim.Flask.FlaskApp import FlaskAppWrapper
        # if not set as path variable
        # owlready2.owlready2.JAVA_EXE = java path

        # path to example

        from ontologysim.ProductionSimulation.init.Initializer import Initializer

        init = Initializer(current_dir)

        production_config_path = (
            "/ontologysim/Flask/Assets/DefaultFiles/production_config_lvl3.ini"
        )
        owl_config_path = "/ontologysim/Flask/Assets/DefaultFiles/owl_config.ini"
        controller_config_path = (
            "/ontologysim/Flask/Assets/DefaultFiles/controller_config.ini"
        )
        logger_config_path = "/ontologysim/Flask/Assets/DefaultFiles/logger_config_lvl3.ini"
        a = FlaskAppWrapper(
            "wrap",
            init,
            {
                "production": production_config_path,
                "owl": owl_config_path,
                "controller": controller_config_path,
                "logger": logger_config_path,
            },
        )
        a.addSwaggerUI()
        a.run(args.bind, args.port)

    elif args.command == "export-ontology":
        from ontologysim.ProductionSimulation.sim.SimCore import SimCore

        sim_core = SimCore()
        sim_core.createOWLStructure()
        sim_core.save_ontology(args.outfile)
    elif args.command == "help":
        parser.print_help()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
