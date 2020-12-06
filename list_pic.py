
import os
import shutil

dst_dir = './imgs/'
def getFileList(dir, Filelist, ext=None):
    """
    获取文件夹及其子文件夹中文件列表
    输入 dir：文件夹根目录
    输入 ext: 扩展名
    返回： 文件路径列表
    """
    newDir = dir
    if os.path.isfile(dir):
        if ext is None:
            Filelist.append(dir)
        else:
            if ext in dir[-3:]:

                Filelist.append(dir)
                shutil.copy(dir,dst_dir+(str(dir).split("\\")[-1]))

    elif os.path.isdir(dir):
        for s in os.listdir(dir):
            newDir = os.path.join(dir, s)
            getFileList(newDir, Filelist, ext)
    return Filelist


if __name__ == '__main__':
    org_img_folder = r'C:\Users\77558\Desktop\120_d1d5b411fa37603c4eca6c9249333bbd'


# 检索文件
    imglist = getFileList(org_img_folder, [], 'png')
    print('本次执行检索到 ' + str(len(imglist)) + ' 个jpg文件\n')

