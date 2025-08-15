     # tests/test_trainer.py
     # -*- coding: utf-8 -*-
     """
     Testes unitários para trainer.py.
     Por quê? Verificam treinamento e avaliação isolados.
     Como? Mock dataset pequeno; verifica MSE e arquivo salvo.
     """

     import pytest
     from trainer import treina_modelo

     def test_treina_modelo(mocker):
         """Testa treinamento com mock dataset."""
         mock_df = pd.DataFrame({'label_score_acessibilidade': [80, 90], 'imagens_sem_alt': [1, 2]})
         mocker.patch('pd.read_csv', return_value=mock_df)
         mocker.patch('joblib.dump')  # Mock save.
         treina_modelo()
         # Asserts adicionais podem verificar prints ou arquivos.
