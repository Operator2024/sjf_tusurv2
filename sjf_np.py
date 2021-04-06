import time
from os import getppid, remove
from random import randint
from re import split, sub
from threading import Thread, current_thread
from typing import NoReturn, Any, Dict, List, Tuple

import numpy as np


def worker(burstTime: float) -> NoReturn:
    print(space, burstTime, space, "Thread worked", space, current_thread().name)
    time.sleep(burstTime)
    print(space, burstTime, space, "Thread stop", space, "  ", current_thread().name)


def choosing(p: Tuple, students: Dict, threadlist: List) -> List:
    _tList = threadlist
    if len(p[1]) != 3:
        # example tuple - ('Prep1', ['Dis1', 1])
        # добавляем параметр обозначающий количество свободных мест
        p[1].append(p[1][1])
    # milliseconds
    mBurstTime = 99999999
    pCandidateName: Any = None
    pCandidatePrior: Any = None

    for i in range(0, p[1][1]):
        if p[1][2] > 0:
            for stud in students:
                # Set max priority for a student in case with condition below
                if students[stud]["Priority"] > MPriority:
                    students[stud]["Priority"] = MPriority

                if students[stud].get("Used") is None:
                    if p[1][0] in students[stud]["Discipline"]:
                        if ArrivalTime >= students[stud]["ArrivalTime"]:
                            if pCandidatePrior is None:
                                if students[stud]["BurstTime"] < mBurstTime:
                                    mBurstTime = students[stud]["BurstTime"]
                                    pCandidateName = stud
                                    pCandidatePrior = students[stud]["Priority"]
                            elif pCandidatePrior <= MPriority and pCandidatePrior == students[stud]["Priority"]:
                                # Баг с приоритетом, и временем, bugfix
                                if students[stud]["BurstTime"] < mBurstTime:
                                    mBurstTime = students[stud]["BurstTime"]
                                    pCandidateName = stud
                                    pCandidatePrior = students[stud]["Priority"]
                            elif pCandidatePrior <= MPriority and pCandidatePrior < students[stud]["Priority"]:
                                mBurstTime = students[stud]["BurstTime"]
                                pCandidateName = stud
                                pCandidatePrior = students[stud]["Priority"]

                elif students[stud].get("Used") is not None:
                    if students[stud]["Used"] is False:
                        if ArrivalTime >= students[stud]["ArrivalTime"]:
                            if p[1][0] in students[stud]["Discipline"] and p[1][0] not in students[stud]["DisciplineFinished"]:
                                if pCandidatePrior is None:
                                    if students[stud]["BurstTime"] < mBurstTime:
                                        mBurstTime = students[stud]["BurstTime"]
                                        pCandidateName = stud
                                        pCandidatePrior = students[stud]["Priority"]
                                elif pCandidatePrior <= MPriority and pCandidatePrior == students[stud]["Priority"]:
                                    if students[stud]["BurstTime"] < mBurstTime:
                                        mBurstTime = students[stud]["BurstTime"]
                                        pCandidateName = stud
                                        pCandidatePrior = students[stud]["Priority"]
                                elif pCandidatePrior <= MPriority and pCandidatePrior < students[stud]["Priority"]:
                                    mBurstTime = students[stud]["BurstTime"]
                                    pCandidateName = stud
                                    pCandidatePrior = students[stud]["Priority"]
            if pCandidateName is not None:
                students[pCandidateName]["Used"] = True
                # _tList.append(f"{pCandidateName}.{s[pCandidateName]['Group']}.{p[1][0]}")
                _tList.append(Thread(target=worker, args=(students[pCandidateName]["BurstTime"] / 1000.0,),
                                     name=f"{pCandidateName}.{students[pCandidateName]['Group']}.{p[1][0]}"))
                # part petri net
                p[1][2] -= 1
                pCandidateName = None
                pCandidatePrior = None
    return _tList


def logger(quantNumber: float, threadlist: List, students: Dict, of, times) -> NoReturn:
    PPID: int = getppid()
    print(f"Номер кванта - {quantNumber}, Текущей unixtime - {times}", file=of)
    usedStudent = set()

    for th in threadlist:
        _studname, _studgroup, _studdis = split("\.", th.name)
        usedStudent.add(_studname)
        # th.pid
        # if studDict[_studname]["LT"] != 999:
        print(f"Студент - {_studname} группа {_studgroup} сдает дисциплину {_studdis}, TID - {th.ident}, Parent PID - {PPID}", file=of)
    for _stud in students:
        if _stud not in usedStudent:
            if students[_stud].get("Used") is None:
                if ArrivalTime >= students[_stud]["ArrivalTime"]:
                    print(f"Студент - {_stud} группа {students[_stud]['Group']} готов к сдаче дисциплин, но ожидает очереди", file=of)
                else:
                    print(f"Студент - {_stud} группа {students[_stud]['Group']} ещё не прибыл на сдачу дисциплин", file=of)
            elif students[_stud].get("Used") is not None:
                if students[_stud]["Used"] is False:
                    if len(students[_stud]["Discipline"]) == len(students[_stud]["DisciplineFinished"]):
                        print(f"Студент - {_stud} группа {students[_stud]['Group']} закончил сдачу всех дисциплин", file=of)
                    elif len(students[_stud]["Discipline"]) != len(students[_stud]["DisciplineFinished"]):
                        for d in students[_stud]["Discipline"]:
                            if d not in students[_stud]["DisciplineFinished"]:
                                print(f"Студент - {_stud} группа {students[_stud]['Group']} ожидает сдачу дисциплины {d}", file=of)
    del usedStudent


def read_data(of, fname='input.txt') -> Tuple:
    '''
    The func is reading data from input.txt file.
    If some data was omitted then they will be generated.
    Function returns class instance or SJFnp (sjf non-preemptive) either SJPp (sjf preemptive)
    '''
    with open(fname) as f:
        _PA = int(f.readline().strip('\n'))
        _QT = float(f.readline().strip('\n')) / 1000
        _MaxT = int(f.readline().strip('\n'))
        _MaxP = int(f.readline().strip('\n'))
        _NR = int(f.readline().strip('\n'))
        ArgsR = [list(f.readline().strip('\n') for _ in range(3)) for i in range(_NR)]
        _NP = int(f.readline().strip('\n'))
        ArgsP = [list(f.readline().strip('\n') for _ in range(6)) for i in range(_NP)]

    ArgsProf = list(map(lambda x: [str(x[0]), str(x[1]), int(x[2]) if x[2] != '' else ''], ArgsR))
    ArgsStud = list(map(lambda x: [
        str(x[0]),
        str(x[1]),
        x[2].split(),
        float(x[3]) / float(1000) if x[3] != '' else '',
        int(x[4]) if x[4] != '' else '',
        float(x[5]) / float(1000) if x[5] != '' else ''], ArgsP))

    # Exists names prof and disciplines:
    used_profnames = [e[0] for e in ArgsR]
    used_studnames = [e[0] for e in ArgsP]

    used_disc = np.unique([ds for d in (list(e[2]) for e in ArgsStud) for ds in d])
    if len(used_disc) == 0:
        used_disc = ['D1', 'D2', 'D3']
    used_disc_by_prof = [e[1] for e in ArgsProf if e[1] != '']

    profUniqueName = 1
    # Generate random data for professor
    for p in ArgsProf:
        trigger = False
        if p[0] == '':
            while True:
                profName = 'P' + str(profUniqueName)
                if profName not in used_profnames:
                    break
            p[0] = profName
        if p[1] == '':
            for i in used_disc:
                if i not in used_disc_by_prof:
                    if trigger is False:
                        used_disc_by_prof.append(i)
                        p[1] = i
                        trigger = True
        if p[2] == '':
            # Generate random count simultaneous students
            p[2] = randint(1, 4)

    studentUniqueName = 1
    # Generate random data for student
    for p in ArgsStud:
        if p[0] == '':
            while True:
                studName = 'S' + str(studentUniqueName)
                studentUniqueName += 1
                if studName not in used_studnames:
                    break
            p[0] = studName
        if p[1] == '':
            p[1] = 'G1'
        if p[2] == '':
            p[2] = [used_disc[randint(0, len(used_disc) - 1)]]
        if p[3] == '':
            p[3] = randint(1, _MaxT) / 1000
        if p[4] == '':
            p[4] = randint(1, _MaxP)
        if p[5] == '':
            p[5] = randint(1, 5 * _MaxT) / 1000

    print(_NR, file=of)
    for l in ArgsProf:
        print(*map(str, l), sep='\n', file=of)
    print(_NP, file=of)
    for l in ArgsStud:
        print(*map(str, l), sep='\n', file=of)
    print('STOP', file=of)

    _Professor = {}
    _Student = {}

    for i in ArgsProf:
        _Professor[i[0]] = [i[1], i[2]]

    for i in ArgsStud:
        _Student[i[0]] = {"Group": i[1], "Discipline": i[2], "BurstTime": i[3] * 1000, "Priority": i[4], "ArrivalTime": i[5] * 1000}

    return _PA, _QT * 1000, _MaxT, _MaxP, _NR, _NP, _Professor, _Student, of


if __name__ == '__main__':
    pList = []
    pRunList = []
    of = open("_tmp_output.txt", "w+", encoding="UTF-8")
    PA, QTime, MaxT, MPriority, NR, NP, Professors, Students, of = read_data(of)

    # with open("input.json") as ifstream:
    #     _tmp = json.load(ifstream)
    #     QTime = _tmp["QTime"] / 1000.0
    #     MPriority = _tmp["MPriority"]
    #     SJF_mode = _tmp["SJF_mode"]
    #     Professors = _tmp["Professors"]
    #
    # with open("example.json") as ifstream:
    #     Student = json.load(ifstream)
    #

    # print(Professors, "Professors")
    # print(Students, "Student")
    # в цикле для каждого препода проверяем наличие места у него и в случае его наличия делаем следующее
    # проверяем занят ли студент каким либо другим преподом
    # если не занят, то проверяем наличие необходимой для препода дисциплины
    # если есть, то помечаем его как кандидата, и ищем дальше свободного студента с меньшим burstTime
    # после просмотра всех свободных студентов создаем поток для отобранного студента
    #
    #
    #

    StartTime = 0
    QTimeDiff = 0
    ProcessingStudents = set()
    QuantNumber = 0
    ArrivalTime = 0
    space = " " * 6
    print(f"Time sleep in ms |{space}Status{space}| Thread name")
    while True:
        for i in Professors:
            a = choosing((i, Professors[i]), Students, pList)
            pList = a

        for p in pList:

            if StartTime == 0:
                StartTime = round(time.time(), 2)
                QTimeDiff = StartTime + (QTime / 1000.0)

            p.start()

            pRunList.append(p)
            # pList.remove(p)
        pList.clear()
        for r in pRunList:
            if r.is_alive() is False:
                _tmp_thread_info = split("\.", r.name)
                Students[_tmp_thread_info[0]]["Used"] = False
                if Students[_tmp_thread_info[0]].get("DisciplineFinished") is None:
                    Students[_tmp_thread_info[0]]["DisciplineFinished"] = [_tmp_thread_info[2]]
                else:
                    Students[_tmp_thread_info[0]]["DisciplineFinished"].append(_tmp_thread_info[2])
                # Petri net
                for prof in Professors:
                    if Professors[prof][0] == _tmp_thread_info[2]:
                        Professors[prof][2] += 1
                pRunList.remove(r)

        for k in Students:
            if Students[k].get("DisciplineFinished") is not None:
                if len(Students[k]["Discipline"]) == len(Students[k]["DisciplineFinished"]):
                    # print(Students[k]["Discipline"], " - ", Students[k]["DisciplineFinished"], Students)
                    if Students[k]["Used"] is False and k not in ProcessingStudents:
                        ProcessingStudents.add(k)

        # bugfix
        if len(ProcessingStudents) == len(Students):
            QuantNumber += 1
            totalTime = round(time.time() - StartTime, 3)
            logger(QuantNumber, pRunList, Students, of, totalTime)
            print(f"Total time - {totalTime}")
            of.close()
            break

        c_time = round(time.time(), 2)
        if c_time >= QTimeDiff:
            QTimeDiff = c_time + (QTime / 1000.0)
            ArrivalTime += QTime
            QuantNumber += 1
            logger(QuantNumber, pRunList, Students, of, c_time)

    with open("_tmp_output.txt", "r", encoding="UTF-8") as tmpstream:
        _output = tmpstream.read()
        _output = sub("STOP", str(totalTime), _output)
        with open("output.txt", "w+", encoding="UTF-8") as outstream:
            outstream.write(_output)
    remove("_tmp_output.txt")
