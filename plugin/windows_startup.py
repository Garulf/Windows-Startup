from flox import Flox

import startup

class WindowsStartup(Flox):

    def query(self, query):
        programs = startup.get_startup_programs()
        for program in programs:
            if query.lower() in program.name.lower():
                subtitle = f"❌{program.status}"
                if program.value():
                    subtitle = f"✔️{program.status}"
                _ = self.add_item(
                    title=program.name.replace(".lnk", ""),
                    subtitle=subtitle,
                    icon=program.path,
                    method='toggle',
                    parameters=[str(program._base_key), str(program._reg_path), str(program._key_index)]
                )
                # self.logger.info(str(program._base_key), str(program._reg_path), str(program._key_index))

    def context_menu(self, data):
        pass

    def toggle(self, base_key, path, key_index):
        prog = startup.StartupProgram(int(base_key), path, int(key_index))
        prog.toggle()


if __name__ == "__main__":
    WindowsStartup()
