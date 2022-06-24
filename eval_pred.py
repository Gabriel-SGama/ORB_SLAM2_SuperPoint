import os
from glob import glob
import numpy as np

GT_POS_DIR = "/home/gama/Documentos/datasets/kitti/data_odometry_poses/dataset/poses/"
PATH_TO_SEQ = "/home/gama/Documentos/datasets/kitti/data_odometry_color/dataset/sequences/"


def createGTFile(tumFile, gtFile, timeFile, savePath):
    with open(tumFile) as tf:
        tlinesA = tf.readlines()

    with open(gtFile) as gtf:
        gtlinesA = gtf.readlines()

    with open(timeFile + "times.txt") as tif:
        tilinesA = tif.readlines()

    print(gtFile)
    gtlinesA = [line for line in gtlinesA]
    print(len(gtlinesA))
    tilinesA = [line for line in tilinesA]
    print(len(tilinesA))
    tlines = [line.split(" ")[0] for line in tlinesA]  # gets time stamp
    idx = 0

    gtklines = []
    for tline in tlines:
        while abs(float(tilinesA[idx]) - float(tline)) > 0.00001:
            idx += 1

        gtklines.append(gtlinesA[idx])
        idx += 1

    print("savePath:", savePath)
    with open(savePath, "w") as fp:
        fp.write("".join(gtklines))
        fp.flush()


def saveResults(pathKittiFile, gtkFile, pathToplot):
    os.makedirs(pathToplot, exist_ok=True)

    run = pathKittiFile.split("/")[-1].split(".")[0].split("_")[0]
    model = pathKittiFile.split("/")[-2]
    seq = pathKittiFile.split("/")[-3]

    os.system(
        "yes | evo_traj kitti "
        + pathKittiFile
        + " --ref="
        + gtkFile
        + " -s -a --plot_mode=xz --save_plot "
        + pathToplot
        + run
        + ".png"
    )

    os.system(
        "yes | evo_ape kitti "
        + gtkFile
        + " "
        + pathKittiFile
        + " -s -a -va --plot_mode xz --save_plot "
        + pathToplot
        + run
        + ".png --save_results results/"
        + seq
        + "/"
        + model
        + "/"
        + run
        + "ape_res.zip"
    )


if __name__ == "__main__":

    results_path = "results/"

    folders = []
    print("eval results in directorys:")
    for it in os.scandir(results_path):
        if it.is_dir():
            for it2 in os.scandir(it.path):
                folders.append(it2.path)
                print(it2.path)

    for folder in folders:
        seq = folder.split("/")[-2]
        model = folder.split("/")[-1]
        gtFile = results_path + seq + "/" + model + "/" + "gt_pos.txt"
        os.system("cp " + GT_POS_DIR + seq + ".txt " + results_path + seq + "/" + model + "/" + "gt_pos.txt")
        run_files = glob(folder + "/*.txt")
        run_files = [file for file in run_files if file.split("/")[-1].split(".")[0].isdigit()]

        # print(run_files)
        for rfile in run_files:
            run_number = rfile.split("/")[-1].split(".")[0]
            os.system("yes | evo_traj tum " + rfile + " --save_as_kitti")  # convert to kitti config
            pathKittiFile = "".join(map(str, rfile.split(".")[:-1])) + "_kitti.txt"
            os.system("mv " + run_number + ".kitti " + pathKittiFile)

            gtkFile = "".join(map(str, rfile.split(".")[:-1])) + "_kgt.txt"
            createGTFile(rfile, gtFile, PATH_TO_SEQ + seq + "/", gtkFile)

            saveResults(pathKittiFile, gtkFile, folder + "/plots/")
