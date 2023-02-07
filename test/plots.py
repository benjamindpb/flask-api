import matplotlib.pyplot as plt
import pandas as pd

LABELS_DF = pd.read_csv("labels/labels_perf.tsv", sep='\t')
AUTO_DF = pd.read_csv("performance/autocomplete.tsv", sep='\t')
DUMP_DF = pd.read_csv('performance/performance.tsv', sep='\t')


def dumps_performance(df : pd.DataFrame):
    df_gz = df[df['cf  '] == 'gz  ']
    df_bz = df[df['cf  '] == 'bz2 '] 
    plt.plot(df_gz['n_p625  '], df_gz['time     '], marker='s', c="c", label='gzip', markersize=7)
    plt.plot(df_bz['n_p625  '], df_bz['time     '], marker='^', markersize=7, c="m", label='bzip2')
    plt.yscale('linear')
    plt.legend(loc='lower right', ncol=2, fontsize=10, title='Formato de compresión')
    plt.title('Rendimiento del analisis del dump de Wikidata')
    plt.xlabel("# de entidades")
    plt.ylabel('Tiempo de ejecución (s)')
    plt.grid()
    plt.show()


def box_plot(df: pd.DataFrame):
    df_pos = df[df['results'] >= 0]
    # data = normalize_time(df_pos)['time']
    plt.figure()
    plt.title('Tiempo de ejecución de busquedas de etiquetas')
    plt.boxplot(df['time'], vert=False, widths=0.3, patch_artist=True)
    # plt.xscale('log')
    plt.xlabel('Tiempo (s)')
    plt.show()


def scatter_plot_labels(df : pd.DataFrame):
    df_pos = df[df['results'] >= 0]
    df_neg = df[df['results'] < 0]
    plt.grid()
    plt.scatter(df_pos['time'], df_pos['results'], c=df_pos['results'], cmap='viridis_r')
    plt.scatter(df_neg['time'], df_neg['results'], c='r', label='HTTP 500')
    plt.xlabel('Tiempo (s)')
    plt.ylabel('# de entidades')
    plt.title('Tiempo de obtención de resultados de consulta SPARQL')
    plt.legend(loc='upper right', ncol=2)
    plt.colorbar()
    plt.show()

def scatter_plot_autocomplete(df : pd.DataFrame):
    len1 = df[df['length'] == 1]
    len2 = df[df['length'] == 2]
    # len3 = df[df['length'] == 3]
    # plt.scatter(len3['time'], len3['results'], c='purple', label='length 3')
    plt.scatter(len2['time'], len2['results'], c='blueviolet', label='length 2')
    plt.scatter(len1['time'], len1['results'], c='darkorange', label='length 1')
    plt.title('Tiempo de ejecución de autocompletado')
    plt.xlabel('Tiempo (s)')
    plt.ylabel('# de entidades')
    plt.legend(loc='center right', ncol=2, title='Largo de busqueda')
    plt.grid()
    plt.show()

def box_plot_autocomplete_length(df : pd.DataFrame):
    len1 = df[df['length'] == 1]
    len2 = df[df['length'] == 2]

    data = [len1['time'], len2['time']]
    
    fig = plt.figure()
    
    # Creating axes instance

    plt.boxplot(data, vert=False, patch_artist=True, labels=['1', '2'], widths=0.75) 
    plt.ylabel("Largo de busqueda")
    plt.xlabel('Tiempo (s)')
    plt.title("Tiempo de ejecución de autocompletado")

    # plt.subplot(3, 1, 1)
    # plt.boxplot(len1['time'], notch=False, vert=False, widths=0.5)
    # plt.ylabel("HOLA")
    # plt.subplot(3, 1, 2)
    # plt.boxplot(len2['time'], notch=False, vert=False, widths=0.5)
    # plt.subplot(3, 1, 3)
    # plt.boxplot(len3['time'], notch=False, vert=False, widths=0.5)
    # plt.xlabel('(s)')
    plt.show()



# dumps_performance(DUMP_DF)
# box_plot(LABELS_DF)
# scatter_plot_labels(LABELS_DF)
# scatter_plot_autocomplete(AUTO_DF)
box_plot_autocomplete_length(AUTO_DF)