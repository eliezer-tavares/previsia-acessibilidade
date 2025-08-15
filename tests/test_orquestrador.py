     # tests/test_orquestrador.py
     # -*- coding: utf-8 -*-
     """
     Testes de integração para orquestrador.py.
     Por quê? Verificam fluxo completo (leitura, coleta paralela, salva), com mocks para evitar rede real.
     Como? Mock analisar_url_completa para retornar dados falsos; verifica CSV gerado.
     """

     import pytest
     import os
     from orquestrador import gera_dataset

     def test_gera_dataset(tmpdir, mocker):  # Tmpdir: pasta temp de pytest.
         """Testa geração de dataset com batch pequeno."""
         mocker.patch('pd.read_csv', return_value=pd.DataFrame({'0': ['https://example.com']}))  # Mock URLs.
         mocker.patch('collector.analisar_url_completa', return_value={'url': 'test', 'label_score_acessibilidade': 80, 'layout_json': '{}'})
         gera_dataset(batch_size=1)
         assert os.path.exists('data/dataset_acessibilidade.csv')  # Verifica arquivo salvo.
     
