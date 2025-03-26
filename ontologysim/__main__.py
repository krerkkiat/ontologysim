import os
import inspect
import sys
import argparse

def run_simulation(production_config, controller_config, owl_config, logger_config) -> None:
    from ontologysim.ProductionSimulation.init.Initializer import Initializer

    init = Initializer()
    init.initSimCore()

    # choose between load from owl or create from config
    init.createProduction(production_config, owl_config)
    # init.loadProductionFromOWL("ontologysim/example/owl/production_without_task_defect.owl")

    # add Tasks
    init.addTaskPathGiven(production_config)

    # (optional)
    init.addDefectPathGiven(production_config)

    # add Logger
    init.addLoggerAndDataBasePathGiven(logger_config)

    # set controller
    init.loadControllerPathGiven(controller_config)

    # init.set_save_time(400)

    # run Simulation
    init.run()

    # TimeAnalyse.save_dict_to_csv()

    init.s.destroyOnto()


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    run_command_parser = subparsers.add_parser("run", help="Run the simulation.")
    run_command_parser.add_argument("production_config", metavar="PRODUCTION_CONFIG")
    run_command_parser.add_argument("controller_config", metavar="CONTROLLER_CONFIG")
    run_command_parser.add_argument("owl_config", metavar="OWL_CONFIG")
    run_command_parser.add_argument("logger_config", metavar="LOGGER_CONFIG")

    serve_command_parser = subparsers.add_parser("serve", help="Run the development server.")
    serve_command_parser.add_argument("--bind", "-b", default="0.0.0.0")
    serve_command_parser.add_argument("--port", "-p", default=5000, type=int)

    ontology_command_parser = subparsers.add_parser("export-ontology", help="Export the simulation ontology to an RDF file.")
    ontology_command_parser.add_argument("outfile")

    help_command_parser = subparsers.add_parser("help", help="Show this help message.")

    args = parser.parse_args()

    if args.command == "run":
        run_simulation(args.production_config, args.controller_config, args.owl_config, args.logger_config)
    elif args.command == "serve":
        from ontologysim.Flask.FlaskApp import create_app

        app = create_app()
        app.run(args.bind, args.port)
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
