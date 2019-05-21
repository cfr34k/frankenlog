TXT_TEMPLATE = """\
      
      
      
     Name:       {name}
     Anschrift:  {addr}
     Ort:        {qth}
      
      
      
                     Aktivitätswettbewerb Franken                
      
     Call: {my_call}       DOK: {my_dok}          Loc: {my_loc}   
     
     Teilnahmeart: {compo}
     
      
               Band        QSO   Punkte       DOK       Loc
               {band:6s}     {nqsos:4d}   {total_points:6d}     {dok_multi:3d}       {field_multi:3d}  
               _______________________________________________
               Summe      {nqsos:4d}   {total_points:6d}     {dok_multi:3d}       {field_multi:3d}  
               _______________________________________________
      
               Endergebnis:  {total_points} Punkte x {total_multi} Multi = {final_score} Punkte
               _______________________________________________
      
     Ich erkläre, dass ich die Regeln für "Aktivitätswettbewerb Franken"
     beachtet und die Lizenzbestimmungen meines Landes eingehalten habe.
     Die Angaben des Logs entsprechen der Wahrheit.
      
     Ort: {qth}     Datum: {today_de}   Call: {my_call}
      
      
     Dieses ContestLog wurde mit Frankenlog v0.1 erstellt. (https://github.com/cfr34k/frankenlog)
      
      
      
     Aktivitätswettbewerb Franken  -  QSO-Liste     CALL: {my_call}                  
      
     Nr    DATE   UTC  CALL     BAND MODE   SENT                RCVD                  DOK   Loc    Pkt
{qsotable}
      
                                                                          ({dok_multi:5d} + {field_multi:5d}) x {total_points:7d}
      
                                                                             {final_score:15d} Punkte
"""
TXT_SENT_TEMPLATE = "{tx_rst:4s}{tx_num:3s}/{tx_dok}/{tx_loc}"
TXT_RCVD_TEMPLATE = "{rx_rst:4s}{rx_num:3s}/{rx_dok}/{rx_loc}"

TXT_QSO_TEMPLATE = "     {nr:5d} {date:6s} {utc:4s} {call:8s} {band:4s} {mode:6s} {sent:19s} {rcvd:21s} {new_dok:5s} {new_loc:6s} {points:3d}"
