import argparse

from flappy_bat.game.simulation import main

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Flappy Bat AI")
    parser.add_argument("--save", metavar="PATH", default=None, help="Save best network to PATH on each new high score")
    parser.add_argument("--load", metavar="PATH", default=None, help="Load network from PATH and skip initial search")
    parser.add_argument("--record", action="store_true", help="Automatically record every round")
    args = parser.parse_args()
    main(save_path=args.save, load_path=args.load, auto_record=args.record)
