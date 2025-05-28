from collections import defaultdict
import pdfkit
import re

#ei function 3 ta consecutive slot er jonno backtrack korbe
def try_reassign_consecutive_conflict(day, start_hour, target_teacher, course_code, batch_name, used_slots, teacher_availability, depth=0, visited=None):
    if (day, start_hour) not in teacher_availability.get(target_teacher, []):
        print("Slot Nai")
        return False
    print()
    print(f"*****************Recursion a dukhlam******************depth: {depth} ")
    print()
    if visited is None:
        visited = set()
    if depth > 5:
        return False

    slots = [start_hour + i for i in range(3)]
    print()
    print("*********************")
    print(f"Slots: {slots}")
    print("*********************")
    print()

    if any(h not in time_slots for h in slots):
        return False

    state_key = (day, start_hour, target_teacher)
    print()
    print(f"+++++++++++++++++++{state_key}")
    print()
    if state_key in visited:
        return False
    visited.add(state_key)

    print()
    print("Check if all 3 slots are available for target_teacher")
    print()

    available = all(
        (day, h) in teacher_availability.get(target_teacher, []) and
        (day, h) not in used_slots and
        target_teacher not in global_schedule[day][h]['teachers'] and
        batch_name not in global_schedule[day][h]['batches']
        for h in slots
    )

    if available:
        print("*********Give slot directly**********")
        for h in slots:
            routine[batch_name][day][h] = f"{course_code}<br>({target_teacher})"
            used_slots.add((day, h))
            global_schedule[day][h]['teachers'].add(target_teacher)
            global_schedule[day][h]['batches'].add(batch_name)
            print("****************Back to caller************")
        return True

    print("If not available, check if conflicts are same course+teacher")
    conflicts = []
    for h in slots:
        cell = routine[batch_name][day].get(h, '')
        parts = cell.split('<br>')
        if len(parts) != 2:
            return False
        conflict_course = parts[0].strip()
        conflict_teacher = parts[1].strip().strip('()')
        conflicts.append((conflict_course, conflict_teacher))

    
    unique_conflicts = set(conflicts)
    print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    print(f"conflict for teacher: {target_teacher} conflict: {unique_conflicts}")
    print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

    if len(unique_conflicts) != 1:
        print("multiple different conflicts, skip")
        return False

    conflict_course, conflict_teacher = conflicts[0]
    print(f"{conflict_course}, {conflict_teacher}")
    print("find 3 new slots for conflict_teacher")

    for new_day in days:
        new_slots = [14, 15, 16]
        if all(
                (new_day, h) in teacher_availability.get(conflict_teacher, []) and
                (new_day, h) not in used_slots and
                conflict_teacher not in global_schedule[new_day][h]['teachers'] and
                batch_name not in global_schedule[new_day][h]['batches']
                for h in new_slots
            ):
                print("Try Discard")
                for ho in slots:
                    routine[batch_name][day][ho] = ''
                    used_slots.discard((day, ho))
                    global_schedule[day][ho]['teachers'].discard(conflict_teacher)
                    global_schedule[day][ho]['batches'].discard(batch_name)
                print("++++++++discard success+++++++++")

                for ho in new_slots:
                    routine[batch_name][new_day][ho] = f"{conflict_course}<br>({conflict_teacher})"
                    used_slots.add((new_day, ho))
                    global_schedule[new_day][ho]['teachers'].add(conflict_teacher)
                    global_schedule[new_day][ho]['batches'].add(batch_name)

                print("assign the target course")
                for ho in slots:
                    routine[batch_name][day][ho] = f"{course_code}<br>({target_teacher})"
                    used_slots.add((day, ho))
                    global_schedule[day][ho]['teachers'].add(target_teacher)
                    global_schedule[day][ho]['batches'].add(batch_name)
                return True
        


    for new_day in days:
        for idx in range(len(time_slots) - 2):
            new_slots = time_slots[idx:idx + 3]
            if all(
                (new_day, h) in teacher_availability.get(conflict_teacher, []) and
                (new_day, h) not in used_slots and
                conflict_teacher not in global_schedule[new_day][h]['teachers'] and
                batch_name not in global_schedule[new_day][h]['batches']
                for h in new_slots
            ):
                print("Try Discard")
                for ho in slots:
                    routine[batch_name][day][ho] = ''
                    used_slots.discard((day, ho))
                    global_schedule[day][ho]['teachers'].discard(conflict_teacher)
                    global_schedule[day][ho]['batches'].discard(batch_name)
                print("++++++++discard success+++++++++")

                for ho in new_slots:
                    routine[batch_name][new_day][ho] = f"{conflict_course}<br>({conflict_teacher})"
                    used_slots.add((new_day, ho))
                    global_schedule[new_day][ho]['teachers'].add(conflict_teacher)
                    global_schedule[new_day][ho]['batches'].add(batch_name)

                print("assign the target course")
                for ho in slots:
                    routine[batch_name][day][ho] = f"{course_code}<br>({target_teacher})"
                    used_slots.add((day, ho))
                    global_schedule[day][ho]['teachers'].add(target_teacher)
                    global_schedule[day][ho]['batches'].add(batch_name)
                return True

    print("+++++++++++++Recursively try to reassign conflict's conflict++++++++++++++++++++")
    for new_day in days:
        for idx in range(len(time_slots) - 2):
            new_slots = time_slots[idx:idx + 3]
            nested_conflict = False
            if all(hour in time_slots for hour in new_slots):
                ok = try_reassign_consecutive_conflict(
                        new_day, new_slots[0], conflict_teacher, conflict_course,
                        batch_name, used_slots, teacher_availability,
                        depth + 1, visited
                    )
                if not ok:
                    print("###############Recursion Hoyni###############")
                    nested_conflict = True
                    
            if nested_conflict:
                continue

            print("after recursive resolution")
            for h in slots:
                print("&&&&&&&&assign conflict teacher&&&&&&&")
                routine[batch_name][day][h] = ''
                used_slots.discard((day, h))
                global_schedule[day][h]['teachers'].discard(conflict_teacher)
                global_schedule[day][h]['batches'].discard(batch_name)

            for h in new_slots:
                print("&&&&&&add conflict teacher&&&&&")
                routine[batch_name][new_day][h] = f"{conflict_course}<br>({conflict_teacher})"
                used_slots.add((new_day, h))
                global_schedule[new_day][h]['teachers'].add(conflict_teacher)
                global_schedule[new_day][h]['batches'].add(batch_name)

            for h in slots:
                print("&&&&&&add target teacher&&&&&")
                routine[batch_name][day][h] = f"{course_code}<br>({target_teacher})"
                used_slots.add((day, h))
                global_schedule[day][h]['teachers'].add(target_teacher)
                global_schedule[day][h]['batches'].add(batch_name)
            return True

    return False

#ei function randomly jekhane faka pabe seikhane assign korbe
def assign_unassigned_courses(unassigned_courses, routine, days, time_slots, global_schedule):
    for course, slot_e in unassigned_courses:
        teacher = course['teacher']
        course_code = course['code']
        batch_name = None

        for bname, course_list in courses.items():
            if course in course_list:
                batch_name = bname
                break
        if not batch_name:
            continue  

        needed_slots = slot_e
        assigned_slots = 0
        is_even = is_even_course(course_code)

        if is_even:
            found = False
            for day in days:
                for i in range(len(time_slots) - 2):
                    h1, h2, h3 = time_slots[i:i+3]
                    if all( not routine[batch_name][day].get(h) and
                        teacher not in global_schedule[day][h]['teachers'] and
                        batch_name not in global_schedule[day][h]['batches']
                        for h in (h1, h2, h3)
                    ):
                        for h in (h1, h2, h3):
                            routine[batch_name][day][h] = f'{course_code}<br>({teacher})<small><span style="color:red;">(RA)</span></small>'
                            global_schedule[day][h]['teachers'].add(teacher)
                            global_schedule[day][h]['batches'].add(batch_name)
                            assigned_slots += 1
                        found = True
                        break
                if found:
                    break
        
        if not is_even or assigned_slots < needed_slots:
            for day in days:
                for hour in time_slots:
                    if assigned_slots == needed_slots:
                        break
                    if (
                        not routine[batch_name][day].get(hour) and
                        teacher not in global_schedule[day][hour]['teachers'] and
                        batch_name not in global_schedule[day][hour]['batches']
                    ):
                        routine[batch_name][day][hour] = f'{course_code}<br>({teacher})<small><span style="color:red;">(RA)</span></small>'
                        global_schedule[day][hour]['teachers'].add(teacher)
                        global_schedule[day][hour]['batches'].add(batch_name)
                        assigned_slots += 1
                if assigned_slots == needed_slots:
                    break
                

# Utility Functions
def get_initials(name):
    return ''.join(part[0] for part in name.split() if part).upper()

def format_course_info(info):
    if not info or 'No class' in info:
        return 'No class'
    match = re.search(r'\((.*?)\)', info)
    if match:
        full_name = match.group(1)
        initials = get_initials(full_name)
        return info.replace(full_name, initials)
    return info

# Global variables
days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"]
time_slots = [9, 10, 11, 12, 14, 15, 16]

# Helper Functions
def parse_course_code_number(code):
    try:
        return int(code.split()[1])
    except:
        return None

def is_even_course(course_code):
    code_num = parse_course_code_number(course_code)
    return code_num is not None and code_num % 2 == 0

#theory course gular jonno backtracking
def try_reassign_conflicting_slot(day, hour, target_teacher, target_course, conflict_teacher, course_code_, batch_name, used_slots, teacher_availability, depth=0, visited=None):
    if is_even_course(course_code_):
        print("_______prevent for even course___________")
        return False
    
    if visited is None:
        visited = set()

    if depth > 6:
        return False

    state_key = (day, hour, conflict_teacher)
    if state_key in visited:
        return False
    visited.add(state_key)

    print(f"\n{'*'*100}")
    print(f"target teacher: {target_teacher}, conflict teacher: {conflict_teacher}, schedule: ({day}, {hour}), depth: {depth}")
    print(f"{'*'*100}\n")

    print("Try to find a new slot for the conflicting class (non-even courses only)")
    for new_day, new_hour in teacher_availability.get(conflict_teacher, []):
        print(f"Trying to move {course_code_} ({conflict_teacher}) → {new_day} {new_hour}")
        print(" - used slot:", (new_day, new_hour) not in used_slots)
        print(" - not even course:", not is_even_course(course_code_))
        print(" - no teacher conflict:", conflict_teacher not in global_schedule[new_day][new_hour]['teachers'])
        print(" - no batch conflict:", batch_name not in global_schedule[new_day][new_hour]['batches'])

        if (
            (new_day, new_hour) not in used_slots and
            not is_even_course(course_code_) and
            conflict_teacher not in global_schedule[new_day][new_hour]['teachers'] and
            batch_name not in global_schedule[new_day][new_hour]['batches']
        ):
            print("Remove old class")
            routine[batch_name][day][hour] = ''
            used_slots.discard((day, hour))
            global_schedule[day][hour]['teachers'].discard(conflict_teacher)
            global_schedule[day][hour]['batches'].discard(batch_name)

            print("Assign conflicting teacher to new time")
            routine[batch_name][new_day][new_hour] = f"{course_code_}<br>({conflict_teacher})"
            used_slots.add((new_day, new_hour))
            global_schedule[new_day][new_hour]['teachers'].add(conflict_teacher)
            global_schedule[new_day][new_hour]['batches'].add(batch_name)

            print("Assign the target class in now-free slot")
            routine[batch_name][day][hour] = f"{target_course}<br>({target_teacher})"
            used_slots.add((day, hour))
            global_schedule[day][hour]['teachers'].add(target_teacher)
            global_schedule[day][hour]['batches'].add(batch_name)

            return True

    print("Backtracking(recursion)")
    for new_day, new_hour in teacher_availability.get(conflict_teacher, []):
        if (new_day, new_hour) in used_slots:
            cell = routine[batch_name][new_day][new_hour]
            parts = cell.split("<br>")
            if len(parts) != 2:
                continue  # malformed cell
            conflict_course_code_rec = parts[0].strip()
            conflict_teacher_rec = parts[1].strip().strip("()")
            if is_even_course(conflict_course_code_rec):
                print("_______prevent recursion for even course___________")
                continue
            print(f"Recursive check: conflict {conflict_course_code_rec} by {conflict_teacher_rec} at {new_day}, {new_hour}")
            success = try_reassign_conflicting_slot(
                new_day, new_hour,
                conflict_teacher, course_code_,
                conflict_teacher_rec, conflict_course_code_rec,
                batch_name, used_slots, teacher_availability,
                depth + 1, visited
            )

            if success:
                print("after recursive success, now assign main class")
                routine[batch_name][day][hour] = f"{target_course}<br>({target_teacher})"
                used_slots.add((day, hour))
                global_schedule[day][hour]['teachers'].add(target_teacher)
                global_schedule[day][hour]['batches'].add(batch_name)
                return True

    return False


#consecutive slot ffind korbe from 9 to 16
def try_reassign_consecutive_slots(day, start_hour, teacher, batch_name, course_code, used_slots, teacher_availability):
    print(teacher)
    conflict_teachers = []
    flag = False

    for i in range(3):
        hour = start_hour + i
        
        if (day, hour) not in teacher_availability.get(teacher, []):
            print(f"{teacher_availability.get(teacher, [])}")
            return False
        
        entry = routine[batch_name][day].get(hour, '')
        if entry:
            conflict_teacher = entry.split('(')[-1].split(')')[0].strip()
            course_code_ = entry.split('<br>')[0].strip()
            conflict_teachers.append((hour, conflict_teacher, course_code_))
            flag = True

    if flag:
        return False
    for i in range(3):
        hour = start_hour + i
        if teacher in global_schedule[day][hour]['teachers'] or batch_name in global_schedule[day][hour]['batches']:
            print("If block")
            return False

    for i in range(3):
        hour = start_hour + i
        routine[batch_name][day][hour] = f"{course_code}<br>({teacher})"
        used_slots.add((day, hour))
        global_schedule[day][hour]['teachers'].add(teacher)
        global_schedule[day][hour]['batches'].add(batch_name)
    
    return True



#main function
def process_file(path):
    global teacher_rank, teacher_availability, courses, routine, global_schedule
    teacher_rank = {}
    teacher_availability = defaultdict(list)
    courses = defaultdict(list)
    routine = defaultdict(lambda: defaultdict(lambda: defaultdict(str)))
    global_schedule = defaultdict(lambda: defaultdict(lambda: {'teachers': set(), 'batches': set()}))
    cannot_assign_teachers = []
    coordinator_info = {}
    unassigned_courses = []


    with open(path, 'r') as f:
        lines = f.readlines()

    section = None
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue

        if line.lower() == 'teacher_rank':
            section = 'teacher_rank'
            continue
        elif line.lower() == 'teacher_availability':
            section = 'teacher_availability'
            continue
        elif line.lower() == 'courses':
            section = 'courses'
            continue
        elif line.lower() == 'coordinator info':
            section = 'coordinator_info'
            continue
        

        if section == 'teacher_rank':
            name, rank = line.rsplit(' ', 1)
            teacher_rank[name.strip()] = int(rank)
        elif section == 'teacher_availability':
            name, times = line.split(':')
            slots = times.split(',')
            for slot in slots:
                day, hour = slot.strip().split()
                teacher_availability[name.strip()].append((day, int(hour)))
        elif section == 'courses':
            batch, course_list = line.split(':')
            for course_entry in course_list.split(','):
                parts = course_entry.strip().split()
                code = parts[0] + " " + parts[1]
                credit = int(parts[2])
                teacher = " ".join(parts[3:])
                courses[batch.strip()].append({
                    'code': code,
                    'credit': credit,
                    'teacher': teacher
                })
        elif section == 'coordinator_info':
            year, name = line.split(':')
            coordinator_info[year.strip()] = name.strip()


    for batch_name, batch_courses in courses.items():
        used_slots = set()

        even_courses = sorted([c for c in batch_courses if is_even_course(c['code'])],
                              key=lambda x: teacher_rank.get(x['teacher'], 100))
        odd_courses = sorted([c for c in batch_courses if not is_even_course(c['code'])],
                             key=lambda x: teacher_rank.get(x['teacher'], 100))
        print(f"**********Even course: {even_courses}")
        print(f"***********odd course: {odd_courses}")

        for course in even_courses:
            teacher = course['teacher']
            #debug
            print(teacher)
            course_code = course['code']
            assigned = False

            for day in days:
                consecutive_hours = [14, 15, 16]

                if all(
                    (day, hour) in teacher_availability.get(teacher, []) and 
                    (day, hour) not in used_slots and 
                    teacher not in global_schedule[day][hour]['teachers'] and 
                    batch_name not in global_schedule[day][hour]['batches']
                    for hour in consecutive_hours
                    ):
                        for hour in consecutive_hours:
                            routine[batch_name][day][hour] = f"{course_code}<br>({teacher})"
                            used_slots.add((day, hour))
                            global_schedule[day][hour]['teachers'].add(teacher)
                            global_schedule[day][hour]['batches'].add(batch_name)
                        assigned = True
                        break

                if assigned:
                    break
            print("--------------------------------------------------------")
            if not assigned:
                for day in days:
                    for idx in range(len(time_slots) - 2):
                        consecutive_hours = time_slots[idx:idx+3]
                        print(f"{consecutive_hours}, {teacher}, {day}")
                        if all(hour in time_slots for hour in consecutive_hours):
                            success = try_reassign_consecutive_slots(day, consecutive_hours[0], teacher, batch_name, course_code, used_slots, teacher_availability)
                            print(success)
                            print("No Recursion")
                            if success:
                                assigned = True
                                break
                    if assigned:
                        break
            
            if not assigned:
                for day in days:
                    for idx in range(len(time_slots) - 2):
                        consecutive_hours = time_slots[idx:idx+3]
                        print(f"{consecutive_hours}, {teacher}, {day}")
                        if all(hour in time_slots for hour in consecutive_hours):
                            print("NEED RECURSION")
                            success = try_reassign_consecutive_conflict(day, consecutive_hours[0], teacher, course_code, batch_name, used_slots, teacher_availability)
                            if success:
                                assigned = True
                                break
                    if assigned:
                        break


            if not assigned:
                cannot_assign_teachers.append(f"Could not find 3 consecutive slots for {course_code} ({teacher}). Randomly assigned")
                unassigned_courses.append((course, 3))

        for course in odd_courses:
            teacher = course['teacher']
            course_code = course['code']
            needed_slots = course['credit']
            assigned_slots = 0

            for day in days:
                for (availability_day, availability_hour) in teacher_availability.get(teacher, []):
                    if availability_day == day and (day, availability_hour) not in used_slots and \
                        teacher not in global_schedule[day][availability_hour]['teachers'] and \
                        batch_name not in global_schedule[day][availability_hour]['batches']:

                        routine[batch_name][day][availability_hour] = f"{course_code}<br>({teacher})"
                        used_slots.add((day, availability_hour))
                        global_schedule[day][availability_hour]['teachers'].add(teacher)
                        global_schedule[day][availability_hour]['batches'].add(batch_name)
                        assigned_slots += 1
                        if assigned_slots == needed_slots:
                            break
                if assigned_slots == needed_slots:
                    break
            
            print(f"Assigned Slots: {teacher}, {course_code} slot assign hoise: {assigned_slots} ta")
            print("***************************************************************************************")
            print(f"used slots: {used_slots}")
            print("***************************************************************************************")
            
            
            if assigned_slots < needed_slots:
                for (availability_day, availability_hour) in teacher_availability.get(teacher, []):
                    if (availability_day, availability_hour) in used_slots:
                        cell = routine[batch_name][availability_day][availability_hour]
                        conflict_course_code = ""
                        conflict_teacher = ""
                        parts = cell.split("<br>")
                        if len(parts) == 2:
                            conflict_course_code = parts[0].strip()
                            conflict_teacher = parts[1].strip().strip("()")
                        else:
                            print(f"Fix: {cell}")
                    success = try_reassign_conflicting_slot(day=availability_day, hour=availability_hour, target_teacher=teacher, target_course= course_code, conflict_teacher=conflict_teacher, course_code_=conflict_course_code, batch_name=batch_name, used_slots=used_slots, teacher_availability=teacher_availability)
                    print("***************************************************************************************")
                    print(f"used slots: {used_slots}")
                    print("***************************************************************************************")
                    print("*******************************************************")
                    print(f"Teacher Name: {teacher} Conflict Teacher: {conflict_teacher} Schedule: {(availability_day, availability_hour)} code: {course_code}")
                    print("*******************************************************")
                    if success:
                        assigned_slots+=1
                    if assigned_slots == needed_slots:
                            break   
            

            if assigned_slots < needed_slots:
                slot_e = needed_slots - assigned_slots
                cannot_assign_teachers.append(f"Could not find enough slots for {course_code} ({teacher}). Missing {needed_slots - assigned_slots} slots. Randomly assigned.")
                unassigned_courses.append((course, slot_e))

    assign_unassigned_courses(unassigned_courses, routine, days, time_slots, global_schedule)
    html, pdf = generate_output(courses, routine, coordinator_info)
    print(pdf)
    print(html)
    print(cannot_assign_teachers)
    return pdf, html, cannot_assign_teachers

def generate_output(courses, routine, coordinator_info):
    global teacher_rank
    print(teacher_rank)
    teacher_name_short = {}
    for full_name in teacher_rank:
        parts = full_name.split()
        title_short = ''.join([p[0] for p in parts[:-1]])
        name_part = parts[-1]
        short_key = title_short + name_part[0]
        teacher_name_short[short_key] = full_name
    print(teacher_name_short)

    html_content = '''<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
    <title>Class Routine</title><style>
    body { font-family: 'Segoe UI'; margin: 20px; background: #fff; }
    h2, h3 { text-align: center; color: #2c3e50; text-decoration: underline; }
    .routine-container, .teacher-container { width: 100%; background: #fff; border-radius: 12px; padding: 3px 0; margin-bottom: 100px; }
    table { width: 100%; border-collapse: collapse; margin: 10px 0; }
    td { border: 1.5px solid #000; padding: 5px 10px; text-align: center; font-size: 14px; background: #fff; }
    th { border: 1.5px solid #000; padding: 25px 10px; text-align: center; font-size: 14px; background: #2e86de; color: white; }
    .day-cell { background: #6bfeb9; font-weight: bold; }
    .batch-cell { font-weight: bold; background: #8fb3fa; color: #2d3436; }
    .spacer-row td { height: 0%; background: #060606; }
    .break-cell { background: #ff7c53; font-weight: bold; }
    </style></head><body>'''

    html_content += '''<div class="routine-container"><h2>Class Routine</h2><table><tr><th>Day</th><th>Batch</th>'''

    for hour in time_slots:
        if hour < 12:
            html_content += f'<th>{hour}:00 - {hour+1}:00</th>'
        elif hour == 12:
            html_content += '<th>12:00 - 1:00</th><th>1:00 - 2:00</th>'
        else:
            html_content += f'<th>{hour-12}:00 - {hour-12+1}:00</th>'
    html_content += '</tr>'

    for day in days:
        html_content += '<tr class="spacer-row"><td colspan="100%"></td></tr>'
        for idx, batch_name in enumerate(courses):
            html_content += '<tr>'
            if idx == 0:
                html_content += f'<td rowspan="{len(courses)}" class="day-cell">{day}</td>'
            html_content += f'<td class="batch-cell">{batch_name}</td>'
            for hour in time_slots:
                course_info = routine[batch_name][day].get(hour, 'No class')
                course_info = format_course_info(course_info)
                html_content += f'<td>{course_info}</td>'
                if hour == 12:
                    html_content += '<td class="break-cell"><strong>Break</strong></td>'
            html_content += '</tr>'

    html_content += '''
    </table></div><br>
    <div class="teacher-coordinator-container" style="display: flex; justify-content: space-around; align-items: flex-start; gap: 50px; margin-top: 30px;">

        <!-- Teachers Table -->
        <div class="teacher-container">
            <h3 style="text-align: center; color: #2c3e50;">Teachers</h3>
            <table style="width: 100%; border-collapse: collapse; background-color: #aaf1e3; text-align: left;">
                <thead>
                    <tr>
                        <th style="border: 1px solid black; padding: 6px; background-color: #81ecec;">Short Name</th>
                        <th style="border: 1px solid black; padding: 6px; background-color: #81ecec;">Full Name</th>
                    </tr>
                </thead>
                <tbody>
    '''

    for short_key, full_name in teacher_name_short.items():
        html_content += f'<tr><td style="border: 1px solid black; padding: 6px;">{short_key}</td><td style="border: 1px solid black; padding: 6px;">{full_name}</td></tr>'

    html_content += '''
                </tbody>
            </table>
        </div>

        <!-- Coordinators Table -->
        <div class="coordinator-container">
            <h3 style="text-align: center; color: #2c3e50;">Coordinators</h3>
            <table style="width: 100%; border-collapse: collapse; background-color: #ffeaa7; text-align: left;">
                <thead>
                    <tr>
                        <th style="border: 1px solid black; padding: 6px; background-color: #fab1a0;">Year</th>
                        <th style="border: 1px solid black; padding: 6px; background-color: #fab1a0;">Coordinator</th>
                    </tr>
                </thead>
                <tbody>
    '''

    for year, coordinator in coordinator_info.items():
        html_content += f'<tr><td style="border: 1px solid black; padding: 6px;">{year}</td><td style="border: 1px solid black; padding: 6px;">{coordinator}</td></tr>'

    html_content += '''
                </tbody>
            </table>
        </div>

    </div>
    </body></html>
    '''



    with open("class_routine.html", "w", encoding="utf-8") as file:
        file.write(html_content)

    try:
        pdfkit.from_file('class_routine.html', 'class_routine.pdf')
    except OSError:
        config = pdfkit.configuration(wkhtmltopdf=r"C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")
        pdfkit.from_file('class_routine.html', 'class_routine.pdf', configuration=config)
    return 'class_routine.html', 'class_routine.pdf'