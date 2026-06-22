import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from controllers.migracao_controller import MigracaoController

BACKUP_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backup 01.db")

if __name__ == "__main__":
    controller = MigracaoController()
    resultado = controller.importar_backup(BACKUP_PATH)

    print("=" * 60)
    if resultado["sucesso"]:
        print("IMPORTAÇÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 60)
        print(resultado["mensagem"])
    else:
        print("ERRO NA IMPORTAÇÃO!")
        print("=" * 60)
        print(resultado["mensagem"])

    if resultado.get("erros"):
        print("\nAvisos:")
        for erro in resultado["erros"]:
            print(f"  - {erro}")

    input("\nPressione Enter para sair...")
